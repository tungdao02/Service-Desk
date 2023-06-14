from odoo import api, fields, models


class CrmTelecomProvider(models.Model):
    _name = "crm.telecom.provider"
    _description = "Telecom Provider"
    name = fields.Char(string="Telecom Provider Name", required=True, tracking=True)
    prefix_numbers = fields.Char(string="Prefix Number", required=True, tracking=True)
