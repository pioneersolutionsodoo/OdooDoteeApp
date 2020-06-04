# -*- coding: utf-8 -*-
from odoo import api, fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class Partner(models.Model):
#     _name = 'dotee-transact.dotee-transact'
#     _description = 'dotee-transact.dotee-transact'
    _inherit = "res.partner"

    x_customer_payment_id = fields.Char('Property Code')

    # x_studio_computed_charge = fields.Monetary()



#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100