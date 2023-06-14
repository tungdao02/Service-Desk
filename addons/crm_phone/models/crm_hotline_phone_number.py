from odoo import api, fields, models


class CrmHotlinePhoneNumber(models.Model):
    _name = "crm.hotline.phone.number"
    _description = "Telecom Provider"
    phone_number = fields.Char(string="PhoneNumber", required=True, tracking=True)
    prefix_number = fields.Char(string="Prefix Number", required=True, tracking=True)
    telecom_provider_id = fields.Many2one(comodel_name='crm.telecom.provider', string='Telecom Provider')
    team_lead_id = fields.Many2one(comodel_name='crm.team', string='Manager')
    team_member_assigned_id = fields.Many2one(comodel_name='crm.team.member', string='Team member assigned')
