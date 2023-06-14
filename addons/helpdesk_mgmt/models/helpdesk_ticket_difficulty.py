from odoo import fields, models, api


class HelpdeskTicketDifficulty(models.Model):
    _name = "helpdesk.ticket.difficulty"
    _description = "Helpdesk Ticket Difficulty"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    level = fields.Integer(required=True , default=1)
    description = fields.Char(string="Mô tả")