# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from random import randint

from odoo import models, fields, api, _

class User(models.Model):
    _name = 'hr.contract.allowance'
    _description = 'Allowance'



    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string="Tên phụ cấp")
    date_apply = fields.Date(string="Thời gian áp dụng")
    money = fields.Float(string="Số tiền")
    note = fields.Char(string="Phụ cấp")
    color = fields.Integer(string='Color Index', default=_get_default_color)
    contract_ids = fields.Many2many('hr.contract', 'contract_allowance_rel',
                                    'contract_allowance_id', 'contract_id', string='Hợp đồng')


