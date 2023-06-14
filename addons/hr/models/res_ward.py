# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResWard(models.Model):
    _description = 'Ward'
    _name = 'res.ward'

    district_id = fields.Many2one('l10n_pe.res.city.district', string='Huyện', required=True)
    active = fields.Boolean(default=True)
    name = fields.Char(string='Ward Name', required=True)
    code = fields.Char(string='Ward Code', required=True)