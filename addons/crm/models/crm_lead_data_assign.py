from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command
from odoo.exceptions import Warning, UserError, ValidationError


class LeadDataAssignRule(models.TransientModel):

    _name = 'crm.lead.assign.rule'
    _description = "Assign Lead"
    _order = "create_date DESC"
    team_member_id = fields.Many2many('crm.team.member', 'lead_assign_team_member_rel',
                                      'assign_id', 'team_member_id',
                                      string='Assign Team Member', default=None)
    team_id = fields.Many2many('crm.team', 'lead_assign_team_rel', 'assign_id', 'team_id',
                               string='Assign Team', default=None)
    lead_assign_count = fields.Integer(string='Leads Count', default=None)
    campaign_id = fields.Many2one('utm.campaign', string='Campaign', default=None)
    storage_ref_id = fields.Many2one('crm.lead.storage.ref.info', default=None)
    source_id = fields.Many2many('utm.source', 'lead_assign_source_rel', 'assign_id', 'source_id',
                                 string='Source selection', default=None)

    def action_assign_lead_source(self):
        self._cr.execute(
            "select cls.id from crm_lead_storage cls where cls.phone not in "
            "(select phone from crm_lead cl where cl.campaign_id = " + str(self.campaign_id.id) +
            ") and cls.source_id::varchar in "
            "(SELECT a from unnest(string_to_array('"+','.join(str(x) for x in self.source_id.ids) +"', ',')) a)")

        result = self._cr.fetchall()
        #
        # if self.team_id is None & self.team_member_id is None:
        #     raise ValidationError(_("Please choose at least one sale!"))
        count = self.lead_assign_count
        members = []
        if len(self.team_member_id) != 0:
            for team in self.team_id:
                for member in team.member_ids:
                    members.append((team.id, None))
            for member in self.team_member_id:
                members.append((member.crm_team_id.id, member.user_id.id))

        count = min(self.lead_assign_count, len(result))
        vals_array = []
        if len(members) > 0:
            while count > 0:
                for member in members:
                    lead = self.env['crm.lead.storage'].search([('id', '=', result[count - 1][0])])
                    values = {}
                    if lead:
                        values['source_id'] = lead.source_id.id
                        values['name'] = lead.name
                        values['phone'] = lead.phone
                        values['team_id'] = member[0]
                        values['user_id'] = member[1]
                        values['campaign_id'] = self.campaign_id.id
                        vals_array.append(values)
                    count -= 1
                    if count < 0:
                        break
        elif len(self.team_id) > 0:
            index = 0
            team_len = len(self.team_id)
            for lead_id in result:
                lead = self.env['crm.lead.storage'].search([('id', '=', lead_id[0])])
                values = {}
                if lead:
                    values['source_id'] = lead.source_id.id
                    values['name'] = lead.name
                    values['phone'] = lead.phone
                    values['team_id'] = self.team_id[min(index % team_len, team_len - 1)].id
                    values['user_id'] = None
                    values['campaign_id'] = self.campaign_id.id
                    vals_array.append(values)
                index += 1
                if index >= count:
                    break

        self.env['crm.lead'].create(vals_array)
