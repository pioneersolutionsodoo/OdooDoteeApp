# -*- coding: utf-8 -*-

from odoo import api, fields, models, api, _

class Subscription(models.Model):
    _inherit = 'sale.subscription'

    period = fields.Integer('Number of months', default=1)

class SubscriptionLine(models.Model):
#     _name = 'dotee-transact.dotee-transact'
#     _description = 'dotee-transact.dotee-transact'
    _inherit = 'sale.subscription.line'
    
    unit_vacant = fields.Integer('Vacant', store=True, compute='_compute_pricetotal')

    @api.onchange('parent.period')
    @api.depends('unit_vacant', 'price_unit', 'parent.period')
    def _compute_price_unit(self):
        for line in self:
            line.price_unit = line.price_unit * line.order_id.period

    # @api.onchange ('unit_vacant')
    @api.depends('price_unit', 'unit_vacant', 'price_total')
    def _compute_pricetotal(self):
        #"""Compute the amounts of the SO line."""
        for line in self:
            line.price_total -= float(line.unit_vacant * line.price_unit)
                
            # price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            # if line.product_uom_qty and line.receive_in_advance:
            #     price = price - (line.receive_in_advance/line.product_uom_qty)
            # taxes = line.tax_id.compute_all(price, line.order_id.currency_id, product=line.product_id, partner=line.order_id.partner_shipping_id)
            # line.update({
            #     # 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
            #     # 'price_total': taxes['total_included'],
            #     #'unit_vacant': line.unit_vacant,
            #     'price_subtotal': line.price_subtotal - float(line.unit_vacant * line.price_unit),
            # })  

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
