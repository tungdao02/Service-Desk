import datetime
from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError , UserError
from datetime import timedelta

class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _description = "Helpdesk Ticket"
    _rec_name = "number"
    _order = "priority desc, number desc, id desc"
    _mail_post_access = "read"
    _inherit = ["mail.thread.cc", "mail.activity.mixin", "portal.mixin"]

    def _get_default_stage_id(self):
        all_records = self.search([]) 
        return self.env["helpdesk.ticket.stage"].search([], limit =1).id

    
    def _read_group_stage_ids(self, stages, domain, order):

        context = dict(self._context)
        context.setdefault('default_team_id', self.team_id.id)
        team_id = self._context.get('default_team_id')

        record_team_id = self.env["helpdesk.ticket.team"].search([('id' , '=' , team_id)])

        
       
        stage_ids = self.env["helpdesk.ticket.stage"].search([('id' , 'in' , record_team_id.pipeline_id.stages.ids)])
       
        
        print ("team_id :" ,team_id)
        print ("record_team_id :" ,record_team_id.pipeline_id.stages.ids)
        print (stage_ids)
        
        print(stages.pipeline_id.stages.ids)
        
        
        return stage_ids    
    


    number = fields.Char(string="Ticket number", default="/", readonly=True)
    name = fields.Char(string="Title", required=True)
    description = fields.Html(required=True, sanitize_style=True)
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Assigned user",
        tracking=True,
        index=True,
        domain="team_id and [('id', 'in', user_ids)]",  # noqa: B950
        # domain="[('share', '=', False),('id', 'in', user_ids)] or [('share', '=', False)]",  #
        compute = "_compute_leader_id",
        inverse = "_inverse_user_id",
        store = True,
    )
    user_ids = fields.Many2many(
        comodel_name="res.users", related="team_id.user_ids", string="Users"
    )


    assist_user_id = fields.Many2many( comodel_name="res.users", string="Assist Users" )


    stage_id = fields.Many2one(
        comodel_name="helpdesk.ticket.stage",
        string="Stage",
        group_expand="_read_group_stage_ids",
        default=_get_default_stage_id,
        tracking=True,
        ondelete="restrict",
        index=True,
        copy=False,
    )

    partner_id = fields.Many2one(comodel_name="res.partner"  , string="Contact" )
                                #  compute= "_compute_partner_name" , inverse = "_inverse_partner_id")
    partner_name = fields.Char()
    partner_email = fields.Char(string="Email")
    partner_phone = fields.Char(string="Phone")

    last_stage_update = fields.Datetime(default=fields.Datetime.now)
    assigned_date = fields.Datetime()
    closed_date = fields.Datetime()
    closed = fields.Boolean(related="stage_id.closed")
    unattended = fields.Boolean(related="stage_id.unattended", store=True)
    tag_ids = fields.Many2many(comodel_name="helpdesk.ticket.tag", string="Tags")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    channel_id = fields.Many2one(
        comodel_name="helpdesk.ticket.channel",
        string="Channel",
        help="Channel indicates where the source of a ticket"
        "comes from (it could be a phone call, an email...)",
    )
    mother_category_id = fields.Many2one(comodel_name="helpdesk.ticket.mother.category", string="Mother Category" )
    category_id = fields.Many2one(
        comodel_name="helpdesk.ticket.category",
        string="Category",
        domain="[('mother_category_id', '=', mother_category_id)]",
    )
    difficulty_id = fields.Many2one(comodel_name="helpdesk.ticket.difficulty", string="Difficulty" )
    team_id = fields.Many2one(
        comodel_name="helpdesk.ticket.team",
        string="Team",
    )
    priority = fields.Selection(
        selection=[
            ("0", "Low"),
            ("1", "Medium"),
            ("2", "High"),
            ("3", "Very High"),
        ],
        default="1",
    )
    attachment_ids = fields.One2many(
        comodel_name="ir.attachment",
        inverse_name="res_id",
        domain=[("res_model", "=", "helpdesk.ticket")],
        string="Media Attachments",
    )
    color = fields.Integer(string="Color Index")
    kanban_state = fields.Selection(
        selection=[
            ("normal", "Default"),
            ("done", "Ready for next stage"),
            ("blocked", "Blocked"),
        ],
    )
    active = fields.Boolean(default=True)

    timecounter = fields.Float(string='Time Counter', store=True)
    stage_move_date = fields.Datetime(string='Stage Move Date')
    
    previous_stage_id = fields.Many2one( comodel_name="helpdesk.ticket.stage" , compute= "_compute_previous_stage_id" ,string="Previous Stage" , store = True)
    next_stage_id = fields.Many2one( comodel_name="helpdesk.ticket.stage", compute= "_compute_next_stage_id" ,  string="Next Stage" , store = True)

    name_sla = fields.Char()
    status = fields.Selection([('in_progress', 'In Progress'), ('success', 'Success'), ('fail', 'Failed')], default='in_progress',compute="_compute_status", readonly=True)
    sla_model_id = fields.Many2one("helpdesk.ticket.sla.model", string="Kiến trúc SLA")
    from_stage_id = fields.Many2one(comodel_name="helpdesk.ticket.stage", string="Trạng thái bắt đầu")
    to_stage_id = fields.Many2one(comodel_name="helpdesk.ticket.stage", string="Trạng thái kết thúc")

    # ticket_id = fields.Many2one(comodel_name="helpdesk.ticket", string="Yêu cầu")
    # start_date = fields.Datetime(string="Start Date")
    # end_date = fields.Datetime(string="End Date")
    # ticket_id = fields.Many2one(comodel_name="helpdesk.ticket", string="Yêu cầu", )
    explaination = fields.Text(string="Giải trình")
    sla_time = fields.Float(related = "sla_model_id.timelimit" ,string="Thời gian mẫu", widget ="float_time" )
    deadline_datetime = fields.Datetime(string="Thời hạn", compute="_compute_dealinetime", store=True)

    @api.model
    def create(self, vals):
        # Tạo bản ghi mới
        record = super(HelpdeskTicket, self).create(vals)
        
        # Tính toán và cập nhật trường deadline_datetime
        if record.status_stage and record.status_stage == 'In Progress' and record.sla_time:
            created_datetime = datetime.now()
            deadline_datetime = created_datetime + timedelta(hours=record.sla_time)
            record.deadline_datetime = deadline_datetime

        return record
    
    @api.depends("status_stage", "sla_time")
    def _compute_dealinetime(self):
        for record in self:
            if record.status_stage and record.status_stage == "['New']" or not record.status_stage and record.sla_time:
                record.deadline_datetime = False
            elif record.status_stage and record.status_stage == "['In Progress']" and record.sla_time:
                if not record.deadline_datetime:
                    created_datetime = fields.Datetime.now()
                    deadline_datetime = created_datetime + timedelta(hours=record.sla_time)
                    record.deadline_datetime = fields.Datetime.to_string(deadline_datetime)
                else: 
                    record.deadline_datetime =  record.deadline_datetime
            else:
                record.deadline_datetime =  record.deadline_datetime


    @api.depends("deadline_datetime","status_stage")
    def _compute_status(self):
        for record in self:
            if record.deadline_datetime:
                time_now = fields.Datetime.now()
                original_status = record.status
                if record.status_stage == "['Done']":
                    record.status = 'success' 
                elif time_now > record.deadline_datetime and record.status != 'success':
                        record.status = 'fail'
                else: record.status = 'in_progress'
            else: record.status = 'in_progress'


    # sub_ticket = fields.Many2many(comodel_name="helpdesk.ticket" , string="Sub Ticket")
    parent_ticket = fields.Many2one('helpdesk.ticket', string='Parent')
    child_ticket = fields.One2many('helpdesk.ticket', 'parent_ticket', string='Children')
    sla_success_count = fields.Integer(string="SLA Success Count" , compute = "_compute_previous_stage_id" , store = True)
    sla_failed_count = fields.Integer(string="SLA Failed Count" , compute = "_compute_previous_stage_id" , store = True)
    active_time = fields.Float(string='Active Time', store=True, widget = 'float_time')
    active_status = fields.Boolean(string='Active Status', store=True)
    

    
    status_stage = fields.Char(string="Liên quan đến SLA", compute="_compute_stage")

    @api.depends("stage_id.name")
    def _compute_stage(self):
        for record in self:
            if record.stage_id:
                record.status_stage = record.stage_id.mapped('name')

    pipeline_id = fields.Many2one( comodel_name= "helpdesk.ticket.pipeline", related="team_id.pipeline_id")
    # ticket_idd = fields.Many2many("helpdesk.ticket", string="Model ticket")
    # sla_id = fields.One2many( comodel_name= "helpdesk.ticket.sla", inverse_name="ticket_id" , string="SLA")
    # sla_status = fields.Selection([('in_progres' , 'In Progress') , ('failed' , 'Failed') , ('success' , 'Success')], string="SLA Status",  compute = "_compute_sla_status"  , store = True)
    


    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, rec.number + " - " + rec.name))
        return res

    def assign_to_me(self):
        self.write({"user_id": self.env.user.id})


    
   
    @api.depends("stage_id","team_id")
    def _compute_next_stage_id(self):
        for record in self.team_id.pipeline_id.stages:
            if record.sequence == self.stage_id.sequence +1:
                self.write({"next_stage_id": record.id})
               
    
    @api.depends("stage_id")
    def _compute_previous_stage_id(self):
        for record in self.team_id.pipeline_id.stages:
            if record.sequence == self.stage_id.sequence -1 :
                self.write({"previous_stage_id": record.id})


    

        #  holding  code temporary
        # print ("start counting SLA")
        sla_success_count = 0
        sla_failed_count = 0
        for sla in self:
            # print(   self.team_id.pipeline_id.stages)
            if self.stage_id == sla.to_stage_id and self.previous_stage_id == sla.from_stage_id:
                
                if self.assigned_date :
                # self.closed_date
                    delta = fields.Datetime.now() - self.stage_move_date
                    delta = delta.total_seconds() / 3600.0
                    
                    sla_time = sla.sla_model_id.timelimit
                    
                    if delta > sla_time and sla.status != "success" and sla.status != "fail":
                        sla.status = "fail"
                        # print("fail status accessed")
                        # print(sla.status)
                        # print("1.1:" ,sla.status)
                        

                    elif sla.status != "success" and sla.status != "fail":
                        sla.status = "success"
                        # print("success status accessed")
                        # print(sla.status)
                        # print("1.2:", sla.status)
                
              
                elif self.assigned_date  and self.ticket_idd:
                    delta = fields.Datetime.now()  - self.stage_move_date
                    delta = delta.total_seconds() / 3600.0

                    sla_time = sla.sla_model_id.timelimit
                    # print("Delta:", delta)
                    
                    if delta > sla_time and sla.status != "success" and sla.status != "fail":
                        sla.status = "failed"
                        print("2.1:", sla.status)
                        
                    elif sla.status != "success" and sla.status != "fail":
                        sla.status = "success"
                    
                        print("2.2",sla.status)
            if(sla.status == "success"):
                sla_success_count += 1
            
            if(sla.status == "fail"):
                sla_failed_count += 1
        self.sla_success_count = sla_success_count
        self.sla_failed_count = sla_failed_count
                    
                


# //////////////////////////  SLA Status  //////////////////////////

 
    
    #auto assign leader to ticket when team is selected
    @api.depends("team_id", "user_id")
    def _compute_leader_id(self):
        self.user_id = False
        self.user_id = self.team_id.user_id
        
        


    # @api.onchange("team_id")
    # def _compute_team_default_stage_id(self):
    #     for stage in self.team_id.pipeline_id.stages:
    #         if stage.sequence == 1:
    #             self.write({"next_stage_id": stage.id})

            
        
       

    #dissable assigned_user readonly mode in form view
    def _inverse_user_id(self):
        
        return self.team_id.user_id
    
    # delete records everytime user_id changed
    @api.onchange("user_id")
    def _onchange_user_id(self):
        if self.user_id == '':
            self.user_id = False

    # @api.depends("partner_id")
    # def _compute_partner_name(self):
    #     if self.partner_id == :
            
    #         self.partner_id = self.env.user.partner_id.id
    #         self.partner_email = self.partner_id.email
    #         self.partner_name = self.partner_id.name

    # def _inverse_partner_id(self):
    #        return self.partner_id
       
    
    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_name = self.partner_id.name
            self.partner_email = self.partner_id.email

    @api.onchange("mother_category_id")
    def _onchange_mother_category_id(self):
        print(self.category_id.id,  self.mother_category_id.category_ids)
        if self.category_id not in self.mother_category_id.category_ids:
            self.category_id = False
            
        

    # ---------------------------------------------------
    # CRUD
    # ---------------------------------------------------

    def _creation_subtype(self):
        return self.env.ref("helpdesk_mgmt.hlp_tck_created")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("number", "/") == "/":
                vals["number"] = self._prepare_ticket_number(vals)
            if vals.get("user_id") and not vals.get("assigned_date"):
                vals["assigned_date"] = fields.Datetime.now()
            vals["last_stage_update"] = fields.Datetime.now()
            vals["stage_move_date"] = fields.Datetime.now()
            vals["partner_id"] = self.env.user.partner_id.id
            vals["partner_name"] = self.env.user.partner_id.name
            vals["partner_email"] = self.env.user.partner_id.email
        return super().create(vals_list)
    


    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if "number" not in default:
            default["number"] = self._prepare_ticket_number(default)
        res = super().copy(default)
        return res

    def write(self, vals):
        for _ticket in self:
            now = fields.Datetime.now()
            # print(self.previous_stage_id.sequence)
            if vals.get("stage_id"):
                
                context = dict(self._context)
                context.setdefault('default_team_id', self.team_id.id)
                team_id = self._context.get('default_team_id')

                record_team_id = self.env["helpdesk.ticket.team"].search([('id' , '=' , team_id)])

        
       
                stage_ids = self.env["helpdesk.ticket.stage"].search([('id' , 'in' , record_team_id.pipeline_id.stages.ids)])
       
                declined_stage = stage_ids.filtered(lambda r: r.is_declined == True)
                print(declined_stage)
                if vals.get("stage_id") == self.next_stage_id.id and self.next_stage_id.closed == True:
                    counter = 0
                    for sub_ticket in self.child_ticket:
                        print(sub_ticket.name ,sub_ticket.stage_id)
                        if sub_ticket.stage_id.closed == False:
                            counter+=1
                
                    if counter > 0 :
                        raise UserError("your subticket is not finished")
                    print("its next stage time")
                    print(self.next_stage_id.closed)
                elif vals.get("stage_id") == self.next_stage_id.id and self.next_stage_id.closed == False or vals.get("stage_id") == declined_stage.id:
                    print("next stage not closed")

                elif vals.get("stage_id") == self.previous_stage_id.id or vals.get("stage_id") == declined_stage.id:
                    print("its previous stage time")
                    print(self.previous_stage_id.closed)
                else:
                    raise UserError("please don't skip stages and follow the pipeline")
                
                stage = self.env["helpdesk.ticket.stage"].browse([vals["stage_id"]])
                
                vals["stage_move_date"] = self.last_stage_update
                vals["last_stage_update"] = now
                
                if stage.closed:
                    vals["closed_date"] = now
               
            if vals.get("user_id"):
                        vals["assigned_date"] = now
            
            return super().write(vals)

          
                
        

    def action_duplicate_tickets(self):
        for ticket in self.browse(self.env.context["active_ids"]):
            ticket.copy()

    def _prepare_ticket_number(self, values):
        seq = self.env["ir.sequence"]
        if "company_id" in values:
            seq = seq.with_company(values["company_id"])
        return seq.next_by_code("helpdesk.ticket.sequence") or "/"

    def _compute_access_url(self):
        res = super()._compute_access_url()
        for item in self:
            item.access_url = "/my/ticket/%s" % (item.id)
        return res

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------


    def _track_template(self, tracking):
        res = super()._track_template(tracking)
        ticket = self[0]
        if "stage_id" in tracking and ticket.stage_id.mail_template_id:
            res["stage_id"] = (
                ticket.stage_id.mail_template_id,
                {
                    "auto_delete_message": True,
                    "subtype_id": self.env["ir.model.data"]._xmlid_to_res_id(
                        "mail.mt_note"
                    ),
                    "email_layout_xmlid": "mail.mail_notification_light",
                },
            )
        return res

    @api.model
    def message_new(self, msg, custom_values=None):
        """Override message_new from mail gateway so we can set correct
        default values.
        """
        if custom_values is None:
            custom_values = {}
        defaults = {
            "name": msg.get("subject") or _("No Subject"),
            "description": msg.get("body"),
            "partner_email": msg.get("from"),
            "partner_id": msg.get("author_id"),
        }
        defaults.update(custom_values)

        # Write default values coming from msg
        ticket = super().message_new(msg, custom_values=defaults)

        # Use mail gateway tools to search for partners to subscribe
        email_list = tools.email_split(
            (msg.get("to") or "") + "," + (msg.get("cc") or "")
        )
        partner_ids = [
            p.id
            for p in self.env["mail.thread"]._mail_find_partner_from_emails(
                email_list, records=ticket, force_create=False
            )
            if p
        ]
        ticket.message_subscribe(partner_ids)

        return ticket

    def message_update(self, msg, update_vals=None):
        """Override message_update to subscribe partners"""
        email_list = tools.email_split(
            (msg.get("to") or "") + "," + (msg.get("cc") or "")
        )
        partner_ids = [
            p.id
            for p in self.env["mail.thread"]._mail_find_partner_from_emails(
                email_list, records=self, force_create=False
            )
            if p
        ]
        self.message_subscribe(partner_ids)
        return super().message_update(msg, update_vals=update_vals)

    def _message_get_suggested_recipients(self):
        recipients = super()._message_get_suggested_recipients()
        try:
            for ticket in self:
                if ticket.partner_id:
                    ticket._message_add_suggested_recipient(
                        recipients, partner=ticket.partner_id, reason=_("Customer")
                    )
                elif ticket.partner_email:
                    ticket._message_add_suggested_recipient(
                        recipients,
                        email=ticket.partner_email,
                        reason=_("Customer Email"),
                    )
        except AccessError:
            # no read access rights -> just ignore suggested recipients because this
            # imply modifying followers
            return recipients
        return recipients

    # def _notify_get_reply_to(
    #     self, default=None, company=None, doc_names=None  
    # ):
    #     """Override to set alias of tasks to their team if any."""
    #     aliases = (
    #         self.sudo()
    #         .mapped("team_id")
    #         ._notify_get_reply_to(
    #             default=default,  company=company, doc_names=None
    #         )
    #     )
    #     res = {ticket.id: aliases.get(ticket.team_id.id) for ticket in self}
    #     leftover = self.filtered(lambda rec: not rec.team_id)
    #     if leftover:
    #         res.update(
    #             super(HelpdeskTicket, leftover)._notify_get_reply_to(
    #                 default=default,  company=company, doc_names=doc_names
    #             )
    #         )
    #     return res







def _notify_get_reply_to(
        self, default=None, company=None, doc_names=None  ,records=None
    ):
        """Override to set alias of tasks to their team if any."""
        aliases = (
            self.sudo()
            .mapped("team_id")
            ._notify_get_reply_to(
                default=default, records=None, company=company, doc_names=None
            )
        )
        res = {ticket.id: aliases.get(ticket.team_id.id) for ticket in self}
        leftover = self.filtered(lambda rec: not rec.team_id)
        if leftover:
            res.update(
                super(HelpdeskTicket, leftover)._notify_get_reply_to(
                    default=default, records=None, company=company, doc_names=doc_names
                )
            )
        return res
