from odoo import models, fields


class Nation(models.Model):
    _name = 'nation'
    _description = 'Nation'

    code = fields.Char(string='Mã')
    name = fields.Char('Tên')