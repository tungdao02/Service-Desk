
import datetime
from odoo import fields, models, api
from datetime import timedelta



class HelpdeskTicketSLAModel(models.Model):
    _name = "helpdesk.ticket.sla.model"
    _description = "Helpdesk Ticket SLA"
    _order = "sequence, id"


    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    description = fields.Html(string="Mô tả")
    timelimit = fields.Float(string="Thời hạn", widget ="float_time" )
    color = fields.Integer(string="Color Index" , default=1)

    


# class HelpdeskTicketSLA(models.Model):
    # _name = "helpdesk.ticket.sla"
    # _description = "Helpdesk Ticket SLA"
    # _order = "id"
    # _inherit = "helpdesk.ticket"

# #     name = fields.Char()
#     name = fields.Char(string="Title", required=True)
#     name_sla = fields.Char()
#     status = fields.Selection([('in_progress', 'In Progress'), ('success', 'Success'), ('fail', 'Failed')], default='in_progress',compute="_compute_status", readonly=True)
#     sla_model_id = fields.Many2one("helpdesk.ticket.sla.model", string="Kiến trúc SLA")
#     from_stage_id = fields.Many2one(comodel_name="helpdesk.ticket.stage", string="Trạng thái bắt đầu")
#     to_stage_id = fields.Many2one(comodel_name="helpdesk.ticket.stage", string="Trạng thái kết thúc")

#     ticket_id = fields.Many2one(comodel_name="helpdesk.ticket", string="Yêu cầu")
#     start_date = fields.Datetime(string="Start Date")
#     end_date = fields.Datetime(string="End Date")
#     ticket_id = fields.Many2one(comodel_name="helpdesk.ticket", string="Yêu cầu", )
#     explaination = fields.Text(string="Giải trình")
    # sla_time = fields.Float(related = "sla_model_id.timelimit" ,string="Thời gian mẫu", widget ="float_time" )
    # deadline_datetime = fields.Datetime(string="Thời hạn", compute="_compute_dealinetime", store=True)

#     @api.model
#     def create(self, vals):
#         # Tạo bản ghi mới
#         record = super(HelpdeskTicketSLA, self).create(vals)
        
#         # Tính toán và cập nhật trường deadline_datetime
#         if record.ticket_id and record.ticket_id.status_stage == 'In Progress' and record.sla_time:
#             created_datetime = datetime.now()
#             deadline_datetime = created_datetime + timedelta(hours=record.sla_time)
#             record.deadline_datetime = deadline_datetime

#         return record
    
#     @api.depends("ticket_id.status_stage", "sla_time")
#     def _compute_dealinetime(self):
#         for record in self:
#             if record.ticket_id and record.ticket_id.status_stage == "['New']" or not record.ticket_id.status_stage and record.sla_time:
#                 record.deadline_datetime = False
#             elif record.ticket_id and record.ticket_id.status_stage == "['In Progress']" and record.sla_time:
#                 if not record.deadline_datetime:
#                     created_datetime = fields.Datetime.now()
#                     deadline_datetime = created_datetime + timedelta(hours=record.sla_time)
#                     record.deadline_datetime = fields.Datetime.to_string(deadline_datetime)
#                 else: 
#                     record.deadline_datetime =  record.deadline_datetime
#             else:
#                 record.deadline_datetime =  record.deadline_datetime


#     @api.depends("deadline_datetime","ticket_id.status_stage")
#     def _compute_status(self):
#         for record in self:
#             if record.deadline_datetime:
#                 time_now = fields.Datetime.now()
#                 if time_now > record.deadline_datetime:
#                     record.status = 'fail'
#                 elif time_now < record.deadline_datetime and record.ticket_id.status_stage == "['Done']":
#                     record.status = 'success'
#                 else: record.status = 'in_progress'
#             else: record.status = 'in_progress'


    # @api.depends("ticket_id.status_stage", "sla_time", "is_deadline_computed")
    # def _compute_dealinetime(self):
    #     for record in self:
    #         if record.ticket_id and record.ticket_id.status_stage == "['In Progress']" and record.sla_time:
    #             if not record.is_deadline_computed:  
    #                 created_datetime = fields.Datetime.now()
    #                 deadline_datetime = created_datetime + timedelta(hours=record.sla_time)
    #                 record.deadline_datetime = fields.Datetime.to_string(deadline_datetime)
    #                 record.is_deadline_computed = True
    #         else:
    #             record.is_deadline_computed = False
    #             if not record.deadline_datetime:
    #                 record.deadline_datetime = False
   

    # @api.depends("ticket_id.status_stage", "sla_time" )
    # def _compute_dealinetime(self):
    #     for record in self:
    #         if record.ticket_id and record.ticket_id.status_stage == "['In Progress']" and record.sla_time:
    #             if record.deadline_datetime == None:
    #                 created_datetime = fields.Datetime.now()
    #                 deadline_datetime = created_datetime + timedelta(hours=record.sla_time)
    #                 record.deadline_datetime = fields.Datetime.to_string(deadline_datetime)
    #             else: continue
    #         else:
    #             record.deadline_datetime = False
            

    
    # @api.depends("sla_time", "created_datetime")
    # def _compute_dealinetime(self):
    #     for record in self:
    #         if record.created_datetime and record.sla_time:
    #             created_datetime = fields.Datetime.from_string(record.created_datetime)
    #             deadline_datetime = created_datetime + timedelta(hours= record.sla_time)
    #             record.deadline_datetime = fields.Datetime.to_string(deadline_datetime)
    #         else: record.deadline_datetime = False