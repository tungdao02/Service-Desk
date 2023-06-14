from odoo import models, fields


class Religion(models.Model):
    _name = 'religion'
    _description = 'Religion'

    code = fields.Char(string='Mã')
    name = fields.Char('Tên')