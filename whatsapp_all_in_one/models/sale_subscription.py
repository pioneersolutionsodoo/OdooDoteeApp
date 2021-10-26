# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    wp_reminder_sent = fields.Boolean(string='WhatsApp Reminder Sent')

    def _get_default_whatsapp_recipients(self):
        return self.mapped('partner_id')

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