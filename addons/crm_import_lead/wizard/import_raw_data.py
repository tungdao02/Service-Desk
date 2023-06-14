from odoo import api, fields, models


class ImportDuplicatedLead(models.TransientModel):
    _name = 'import.raw.data'
    _description = 'Import Lead'

    phone = fields.Char(string='Phone Number')
    source_id = fields.Char(string='Source Id')
    user_id = fields.Char(string='User Id')
    team_id = fields.Char(string='Team Id')
    name = fields.Char(string='Customer Name')
    reference_id = fields.Many2one(comodel_name='crm.lead.storage.ref.info')
    import_lead_id = fields.Many2one(comodel_name='import.lead')
    duplicated = fields.Boolean(string='Is Duplicated')
