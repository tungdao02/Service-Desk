from odoo import api, exceptions, fields, models, _

class CrmResConfigSettings(models.TransientModel):

    _name = 'crm.res.config.settings'
    _description = "CRM config setting"
    _order = "id desc"
    key = fields.Char('Key')
    value = fields.Char('Value')
