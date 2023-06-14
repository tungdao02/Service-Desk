
from odoo import fields, models


class Tags(models.Model):
    _name = 'slide.tags'
    _description = 'Tags'

    name = fields.Char('Tags')
