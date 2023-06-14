from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command
from odoo.exceptions import Warning, UserError, ValidationError


class TeamAssignRule(models.TransientModel):

    _name = 'crm.team.assign.rule'
    _description = "Assign Lead"
    _order = "create_date DESC"

    team_id = fields.Many2one(comodel_name='crm.team', string='Team')
    auto_assign_all = fields.Boolean(string='Auto assign all leads')
    team_member_ids = fields.Many2many('crm.team.member', 'team_assign_source_rel', 'assign_id',
                                       'member_id', string='Team members', default=None)
    auto_assign_count = fields.Integer(string='Number of leads')

    def action_assign_lead_source(self):
        leads = self.env['crm.lead'].search([('team_id', '=', self.team_id.id), ('user_id', '=', None)])
        team_member_ids = []

        if (not self.auto_assign_all) & len(self.team_member_ids) > 0:
            team_member_ids = self.team_member_ids
        else:
            team_member_ids = self.env['crm.team.member'].search([('crm_team_id', '=', self.team_id.id)])

        leads_count = len(leads) if self.auto_assign_all else min(max(0, self.auto_assign_count), len(leads))
        base_1_index = 1
        members_len = len(team_member_ids)
        for lead in leads:
            lead.update({'user_id': team_member_ids[base_1_index % members_len].user_id})
            base_1_index += 1
            if base_1_index > leads_count:
                break

    def write(self, vals):
        # Your logic goes here or call your method
        super(TeamAssignRule, self).write(vals)
        # Your logic goes here or call your method
        return True
