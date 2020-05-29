# -*- coding: utf-8 -*-
from odoo import api, fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class AccountMoveLine(models.Model):
#     _name = 'dotee-transact.dotee-transact'
#     _description = 'dotee-transact.dotee-transact'
    _inherit = "account.move.line"

    unit_vacant = fields.Integer('Vacant', store=True)



#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100