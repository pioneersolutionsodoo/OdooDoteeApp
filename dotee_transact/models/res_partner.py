# -*- coding: utf-8 -*-
from odoo import api, fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class Partner(models.Model):
#     _name = 'dotee-transact.dotee-transact'
#     _description = 'dotee-transact.dotee-transact'
    _inherit = "res.partner"

    #x_customer_payment_id = fields.Char('Property Code')
    full_formatted_address = fields.Char("Full Address", compute="_get_full_address")
    
    @api.depends('street', 'x_studio_wards_2', 'x_studio_provinces_2')
    def _get_full_address(self):
        for record in self:
            record['full_formatted_address'] = str(record.street) + '\r\n' + str(record.x_studio_wards_2.x_name) + '\r\n' + str(record.x_studio_provinces_2.x_name)
    # x_studio_computed_charge = fields.Monetary()

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
