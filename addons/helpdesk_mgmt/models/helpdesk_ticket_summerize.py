from odoo import models, fields, api

class HelpdeskTicketSumerise(models.Model):
    _name = "helpdesk.ticket.summerize"
    _description = "Helpdesk Ticket Summerize"
    _order = "id"

    sla_success_count = fields.Integer( string = "SLA Success Count" , compute = "_compute_sla_success_count" )
    sla_fail_count = fields.Integer( string = "SLA Fail Count" , compute = "_compute_sla_fail_count" )
    ticket_stage_count = fields.Integer( string = "Ticket Stage Count" , compute = "_compute_ticket_stage_count" )
    ticket_complete_time = fields.Float( string = "Ticket Complete Time" , compute = "_compute_ticket_complete_time" )


    def _compute_sla_success_count(self):
        self.sla_success_count = 10
        # for record in self:
        #     record.sla_success_count = len(self.env['helpdesk.ticket.sla'].search([('status', '=', 'success')]))

    def _compute_sla_fail_count(self):
        self.sla_fail_count = 5
        # for record in self:
        #     record.sla_fail_count = len(self.env['helpdesk.ticket.sla'].search([('status', '=', 'fail')]))

    def _compute_ticket_stage_count(self):
        self.ticket_stage_count = 15

    def _compute_ticket_complete_time(self):
        self.ticket_complete_time = 20