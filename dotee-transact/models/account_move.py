# -*- coding: utf-8 -*-
from odoo import api, fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class AccountMoveLine(models.Model):
#     _name = 'dotee-transact.dotee-transact'
#     _description = 'dotee-transact.dotee-transact'
    _inherit = "account.move.line"

    unit_vacant = fields.Integer('Vacant', store=True)

    x_studio_structure = fields.Char('Structure')

    @api.onchange ('unit_vacant')
    @api.depends('price_unit', 'unit_vacant', 'price_subtotal', 'quantity', 'discount', 'price_unit_wo_discount')
    def _compute_price(self):
        #"""Compute the amounts of the SO line."""
        # AccountTax = self.env['account.tax']
        for line in self:
            if(line.quantity < line.unit_vacant):
                raise ValidationError("Vacant cannot be greater than quantity.")
            # price = AccountTax._fix_tax_included_price(line.price_unit, line.product_id.sudo().taxes_id, AccountTax)
            # line.price_subtotal = line.quantity * price * (100.0 - line.discount) / 100.0
            # line.price_subtotal -= float(line.unit_vacant * line.price_unit)
            line.price_unit_wo_discount = line.price_unit * (1 - (line.discount / 100.0))
            subtotal = line.quantity * line.price_unit_wo_discount
            line.price_subtotal = subtotal - (line.price_unit_wo_discount * line.unit_vacant)
            # price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            # if line.product_uom_qty and line.receive_in_advance:
            #     price = price - (line.receive_in_advance/line.product_uom_qty)
            # taxes = line.tax_id.compute_all(price, line.order_id.currency_id, product=line.product_id, partner=line.order_id.partner_shipping_id)
            # line.update({
            #     # 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
            #     # 'price_total': taxes['total_included'],
            #     # 'unit_vacant': line.unit_vacant,
            #     'price_subtotal': subtotal
            # })  
    
    
    # @api.depends('unit_vacant', 'price_unit', 'quantity', 'discount', 'analytic_account_id.pricelist_id')
    # def _compute_price_subtotal(self):
    #     AccountTax = self.env['account.tax']
    #     for line in self:
    #         price = AccountTax._fix_tax_included_price(line.price_unit, line.product_id.sudo().taxes_id, AccountTax)
    #         line.price_subtotal = line.quantity * price * (100.0 - line.discount) / 100.0
    #         line.price_subtotal -= float(line.unit_vacant * line.price_unit)
    #         if line.analytic_account_id.pricelist_id.sudo().currency_id:
    #             line.price_subtotal = line.analytic_account_id.pricelist_id.sudo().currency_id.round(line.price_subtotal)



#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100