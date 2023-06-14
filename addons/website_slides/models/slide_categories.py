
from odoo import fields, models


class Categories(models.Model):
    _name = 'slide.categories'
    _description = 'Kind of question'

    name = fields.Char('Category name')
    slicetag_id = fields.Many2one('slide.tags', string='Nhãn')
