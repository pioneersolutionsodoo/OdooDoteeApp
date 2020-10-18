# -*- coding: utf-8 -*-

from odoo import models, fields, api

class mis_report(models.Model):
    _inherit = 'mis.report.instance'
    
    def print_report(self):
        return self.env.ref('dotee_transact.dotee_debtor_report').report_action(self)
    
# class dotee-transact(models.Model):
#     _name = 'dotee-transact.dotee-transact'
#     _description = 'dotee-transact.dotee-transact'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
