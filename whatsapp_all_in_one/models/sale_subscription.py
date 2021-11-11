# -*- coding: utf-8 -*-

import base64
import datetime
import logging

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class SaleSubscriptionTemplate(models.Model):
    _inherit = "sale.subscription.template"

    payment_mode = fields.Selection(selection_add=[('send_by_whatsapp', 'Send By WhatsApp')])
    whatsapp_template_id = fields.Many2one(
        'mail.template', string='WhatsApp Template', domain=[('model', '=', 'account.move')],
        default=lambda self: self.env.ref('sale_subscription.mail_template_subscription_invoice', raise_if_not_found=False))


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    wp_reminder_sent = fields.Boolean(string='WhatsApp Reminder Sent')

    def _get_default_whatsapp_recipients(self):
        return self.mapped('partner_id')

    def _recurring_create_invoice(self, automatic=False):
        res = super(SaleSubscription, self)._recurring_create_invoice(automatic)
        auto_commit = self.env.context.get('auto_commit', True)
        cr = self.env.cr
        invoices = self.env['account.move']
        current_date = datetime.date.today()
        imd_res = self.env['ir.model.data']
        template_res = self.env['mail.template']
        if len(self) > 0:
            subscriptions = self
        else:
            domain = [('recurring_next_date', '<=', current_date),
                      '|', ('in_progress', '=', True), ('to_renew', '=', True)]
            subscriptions = self.search(domain)
        if subscriptions:
            sub_data = subscriptions.read(fields=['id', 'company_id'])
            for company_id in set(data['company_id'][0] for data in sub_data):
                sub_ids = [s['id'] for s in sub_data if s['company_id'][0] == company_id]
                subs = self.with_context(company_id=company_id, force_company=company_id).browse(sub_ids)
                context_invoice = dict(self.env.context, type='out_invoice', company_id=company_id, force_company=company_id)
                for subscription in subs:
                    subscription = subscription[0]  # Trick to not prefetch other subscriptions, as the cache is currently invalidated at each iteration
                    if automatic and auto_commit:
                        cr.commit()
                    if subscription.template_id.payment_mode == 'send_by_whatsapp':
                        if not res:
                            try:
                                invoice_values = subscription.with_context(lang=subscription.partner_id.lang)._prepare_invoice()
                                new_invoice = self.env['account.move'].with_context(context_invoice).create(invoice_values)
                                new_invoice.message_post_with_view(
                                    'mail.message_origin_link',
                                    values={'self': new_invoice, 'origin': subscription},
                                    subtype_id=self.env.ref('mail.mt_note').id)
                                invoices += new_invoice
                                next_date = subscription.recurring_next_date or current_date
                                rule, interval = subscription.recurring_rule_type, subscription.recurring_interval
                                new_date = subscription._get_recurring_next_date(rule, interval, next_date, subscription.recurring_invoice_day)
                                subscription.with_context(skip_update_recurring_invoice_day=True).write({'recurring_next_date': new_date})
                                subscription.send_invoice_by_whatsapp(new_invoice)
                                if automatic and auto_commit:
                                    cr.commit()
                            except Exception:
                                if automatic and auto_commit:
                                    cr.rollback()
                                    _logger.exception('Fail to create recurring invoice for subscription %s', subscription.code)
                                else:
                                    raise
                        else:
                            try:
                                next_date = subscription.recurring_next_date or current_date
                                rule, interval = subscription.recurring_rule_type, subscription.recurring_interval
                                new_date = subscription._get_recurring_next_date(rule, interval, next_date, subscription.recurring_invoice_day)
                                subscription.with_context(skip_update_recurring_invoice_day=True).write({'recurring_next_date': new_date})
                                subscription.send_invoice_by_whatsapp(res)
                                if automatic and auto_commit:
                                    cr.commit()
                            except Exception:
                                if automatic and auto_commit:
                                    cr.rollback()
                                    _logger.exception('Fail to create recurring invoice for subscription %s', subscription.code)
                                else:
                                    raise

        return res

    def send_invoice_by_whatsapp(self, invoice):
        self.ensure_one()
        invoice.post()
        IPC = self.env['ir.config_parameter'].sudo()
        dbuuid = IPC.get_param('database.uuid')
        attachments = []
        unique_user = dbuuid + '_2'
        Attachment = self.env['ir.attachment']
        msg = "Dear *" + self.partner_id.name + '*\n'
        msg += 'Invoice *#' + invoice.name + '* for your subscription *' + self.name + '* is here.'
        data = {
            'partner_ids': [(6, 0, self.partner_id.ids)],
            'message': msg,
            'unique_user': unique_user,
        }
        template = self.template_id.invoice_mail_template_id
        report = template.report_template
        report_service = report.report_name

        if report.report_type not in ['qweb-html', 'qweb-pdf']:
            raise UserError(_('Unsupported report type %s found.') % report.report_type)
        res, format = report.render_qweb_pdf([invoice.id])
        res = base64.b64encode(res)
        res_name = 'Invoice_' + invoice.name.replace('/', '_')
        if not res_name:
            res_name = 'report.' + report_service
        ext = "." + format
        if not res_name.endswith(ext):
            res_name += ext
        attachments.append((res_name, res))
        attachment_ids = []
        for attachment in attachments:
            attachment_data = {
                'name': attachment[0],
                'datas': attachment[1],
                'type': 'binary',
                'res_model': invoice._name,
                'res_id': invoice.id,
            }
            attachment_ids.append(Attachment.create(attachment_data).id)
        if attachment_ids:
            data['attachment_ids'] = [(6, 0, attachment_ids)]
        whatsapp_msg_id = self.env['whatsapp.msg'].sudo().create(data)
        wp_msg = whatsapp_msg_id.action_send_msg()

    @api.model
    def _cron_whatsapp_subscription_reminder(self):
        IPC = self.env['ir.config_parameter'].sudo()
        dbuuid = IPC.get_param('database.uuid')
        unique_user = dbuuid + '_2'
        for subscription in self.search([('recurring_next_date', '!=', False), ('partner_id', '!=', False), ('wp_reminder_sent', '=', False)]):
            if subscription.partner_id.mobile and subscription.recurring_next_date  > fields.Date.today() + relativedelta(weeks=-1):
                msg = "Dear *" + subscription.partner_id.name + '*\n'
                msg += 'Your subscription *' + subscription.name + '* is still valid but will be suspended on '
                msg += '*' + str(subscription.recurring_next_date) + '* unless the payment succeeds in the meantime.\nThanks'
                whatsapp_msg_id = self.env['whatsapp.msg'].sudo().create({
                    'partner_ids': [(6, 0, subscription.partner_id.ids)],
                    'message': msg,
                    'unique_user': unique_user,
                    })
                res = whatsapp_msg_id.action_send_msg()
                if res:
                    subscription.wp_reminder_sent = True
        return True
