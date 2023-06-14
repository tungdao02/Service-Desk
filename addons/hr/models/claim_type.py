from odoo import models, fields


class ClaimType(models.Model):
    _name = 'claim.type'
    _description = 'ClaimType'

    code = fields.Char(string='Mã')
    name = fields.Char('Tên')