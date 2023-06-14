from odoo import fields, models, _


class LeadStorageRefInfo(models.Model):
    _name = 'crm.lead.storage.ref.info'
    _description = "Lead/Opportunity reference information"
    _order = "name"
    name = fields.Char('File Name', required=True, readonly=False)
    owner = fields.Many2one('res.users', string='Owner', default=lambda self: self.env.user,
                            domain="['&', ('share', '=', False), ('company_ids', 'in', user_company_ids)]",
                            check_company=True, index=True, tracking=True)
    import_date = fields.Datetime('Imported Date', default=fields.Datetime.now(), readonly=True, copy=False)
    optimize_log = fields.Char('Optimize Log', default='', readonly=True)
    reference_ids = fields.One2many('crm.lead.storage', 'reference_id', string='Lead')

    def action_assign_lead_source(self):
        values = {'storage_ref_id': self.id,
                  'team_id': None,
                  'campaign_id': None}
        data = self.env['crm.lead.assign.rule'].create(values)
        return {
            'name': _('Assign lead'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm.crm_lead_assign_form').id,
            'res_model': 'crm.lead.assign.rule',
            'res_id': data.id,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def unlink(self):
        self.env['crm.lead.storage'].search([('reference_id', '=', self.id)]).unlink()
        return super(LeadStorageRefInfo, self).unlink()

