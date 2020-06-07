# -*- coding: utf-8 -*-

from odoo import api, fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
# from odoo import models, fields, api

class Subscription(models.Model):
    _inherit = 'sale.subscription'

    period = fields.Integer('Number of months', default=1)

class SubscriptionLine(models.Model):
#     _name = 'dotee-transact.dotee-transact'
#     _description = 'dotee-transact.dotee-transact'
    _inherit = 'sale.subscription.line'
    
    unit_vacant = fields.Integer('Vacant', store=True)
    period = fields.Integer(related='analytic_account_id.period', store=True)
    price_subtotal = fields.Float(compute='_compute_price_subtotal', string='Subtotal', digits='Account', store=True)

    @api.onchange('period')
    @api.depends('unit_vacant', 'price_unit', 'period')
    def _compute_price_unit(self):
        for line in self:
            line.price_unit = line.price_unit * line.period
            line.update({
                'price_unit' : line.price_unit
            })

    @api.onchange ('unit_vacant')
    @api.depends('price_unit', 'unit_vacant', 'price_subtotal', 'quantity', 'discount', 'analytic_account_id.pricelist_id')
    def _compute_price(self):
        #"""Compute the amounts of the SO line."""
        AccountTax = self.env['account.tax']
        for line in self:
            if(line.quantity < line.unit_vacant):
                raise ValidationError("Vacant cannot be greater than quantity.")
            price = AccountTax._fix_tax_included_price(line.price_unit, line.product_id.sudo().taxes_id, AccountTax)
            line.price_subtotal = line.quantity * price * (100.0 - line.discount) / 100.0
            line.price_subtotal -= float(line.unit_vacant * line.price_unit)
                
            # price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            # if line.product_uom_qty and line.receive_in_advance:
            #     price = price - (line.receive_in_advance/line.product_uom_qty)
            # taxes = line.tax_id.compute_all(price, line.order_id.currency_id, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                # 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                # 'price_total': taxes['total_included'],
                #'unit_vacant': line.unit_vacant,
                'price_subtotal': line.price_subtotal
            })  

    @api.depends('unit_vacant', 'price_unit', 'quantity', 'discount', 'analytic_account_id.pricelist_id')
    def _compute_price_subtotal(self):
        AccountTax = self.env['account.tax']
        for line in self:
            price = AccountTax._fix_tax_included_price(line.price_unit, line.product_id.sudo().taxes_id, AccountTax)
            line.price_subtotal = line.quantity * price * (100.0 - line.discount) / 100.0
            line.price_subtotal -= float(line.unit_vacant * line.price_unit)
            if line.analytic_account_id.pricelist_id.sudo().currency_id:
                line.price_subtotal = line.analytic_account_id.pricelist_id.sudo().currency_id.round(line.price_subtotal)