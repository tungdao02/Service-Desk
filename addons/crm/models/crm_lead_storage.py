from odoo import api, fields, models, tools, SUPERUSER_ID


class LeadStorage(models.Model):
    _name = 'crm.lead.storage'
    _description = "Lead/Opportunity Storage"
    _inherit = ['crm.lead']
    _order = "priority desc, id desc"
    tag_ids = fields.Char('tag')
    reference_id = fields.Many2one('crm.lead.storage.ref.info', string='Reference Id')

