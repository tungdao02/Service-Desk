from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PhonecallsHotline(models.Model):
    _name = 'crm.phonecalls.hotline'
    _description = 'Hotline'
    name = fields.Char(string='Số hotline', required=True)
    telecom_operator = fields.Selection(
        [('viettel', 'Viettel'), ('vinaphone', 'Vinaphone'),
         ('mobiphone', 'Mobiphone')],
        string='Nhà mạng', required=True)
    manager = fields.Many2one(
        'res.users', string='Người quản lý', compute='_compute_manager', store=True)
    sales_team = fields.Many2one(
        "crm.team", string="Sales team", required=True)

    @api.constrains('name')
    def _check_hotline_number_length(self):
        for record in self:
            if len(str(record.name)) != 11:
                raise ValidationError(
                    "Hotline number must be equal to 11 digits.Currently it is %s digits" % len(str(record.name)))

    @api.depends('sales_team.team_lead_ids')
    def _compute_manager(self):
        for record in self:
            if record.sales_team:
                record.manager = record.sales_team.user_id
            else:
                record.manager = False


class Oddnumber(models.Model):
    _inherit = 'crm.phonecalls.hotline'
    _name = 'crm.phonecalls.oddnumber'
    _description = 'Odd number Management'
    name = fields.Char(string='Số máy lẻ', required=True)
    sales_member = fields.Many2many(
        'res.users', related='sales_team.member_ids', string='Nhân viên sử dụng', required=True)
    selected_sales_member = fields.Many2one(
        'res.users',
        string='Nhân viên sử dụng',
        domain="[('id', 'in', sales_member)]",
        required=True
    )

    telecom_operator = fields.Selection(
        selection_add=[('none', 'None')],
        required=False,
    )

    @api.constrains('name')
    def _check_hotline_number_length(self):
        pass
