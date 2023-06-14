from odoo import api, fields, models, _


class ClaimManagement(models.Model):
    _name = 'claim.management'
    _description = 'ClaimManagement'

    employee_id = fields.Many2one('hr.employee', required=True, default=lambda self: self.env.user.employee_id)
    department_id = fields.Many2one('hr.department', default=lambda self: self.env.user.department_id)
    employee_type = fields.Selection([
        ('employee', 'Employee'),
        ('student', 'Student'),
        ('trainee', 'Trainee'),
        ('contractor', 'Contractor'),
        ('freelance', 'Freelancer'),
    ], string='Chức vụ', default=lambda self: self.env.user.employee_type)
    company_id = fields.Many2one('res.company', 'Công ty', default=lambda self: self.env.user.company_id)
    parent_id = fields.Many2one('hr.employee', 'Chịu trách nhiệm', default=lambda self: self.env.user.parent_id)
    coach_id = fields.Many2one('hr.employee', 'Coach', default=lambda self: self.env.user.coach_id)
    hr_leave_type_id = fields.Many2one('hr.leave.type', store=True, required=True, readonly=False)
    claim_type_id = fields.Many2one('claim.type', store=True, required=True)
    for_reasons = fields.Selection([('1', 'Cá nhân'), ('2', 'Công việc')], string='Vì lý do', default='1')
    start_day = fields.Datetime(string='Ngày bắt đầu')
    end_day = fields.Datetime(string='Ngày kết thúc')
    reasons = fields.Char(string='Lý do')
    time = fields.Float(string='Thời lượng')
    approve = fields.Selection([('yes', 'Có'), ('no', 'Không')], string='Cấp trên duyệt không', default='yes')
    browsing_object = fields.Selection([('NQL', 'Người quản lý'), ('NHD', 'Người hướng dẫn')], string='Đối tượng duyệt', default='NQL')
    approved_by_id = fields.Many2one('hr.employee', compute='_compute_approved_by', default=lambda self: self.env.user.parent_id)
    send_to = fields.Char(string='Gửi tới')
    status = fields.Selection([('A', 'Bản nháp'), ('B', 'Chờ phê duyệt'), ('C', 'Phê duyệt'), ('D', 'Từ chối')], string='Trạng thái', default='A')
    can_draft = fields.Boolean('Bản nháp', compute='_compute_can_draft')
    can_waiting_for_approval = fields.Boolean('Chờ phê duyệt', compute='_compute_can_waiting_for_approval')
    can_approve = fields.Boolean('Đã phê duyệt', compute='_compute_can_approve')
    can_reject = fields.Boolean('Từ chối', compute='_compute_can_reject')
    is_permission = fields.Boolean('Check quyền', default=True, compute='_get_current_user_details')

    @api.depends('browsing_object')
    def _compute_approved_by(self):
        for claim in self:
            manager = claim.browsing_object
            if manager == 'NQL' and not claim.parent_id:
                claim.approved_by_id = claim.parent_id
            elif manager == 'NHD' and not claim.coach_id:
                claim.approved_by_id = claim.coach_id
            else:
                claim.approved_by_id = False
            # if manager and (claim.coach_id == previous_manager or not employee.coach_id):
            #     employee.coach_id = manager
            # elif not employee.coach_id:
            #     employee.coach_id = False

    @api.depends('status')
    def _compute_can_draft(self):
        for claim in self:
            # claim.current_user = self.env.user.employee_id

            if claim.status == 'A':
                claim.can_draft = True
            else:
                claim.can_draft = False
        # self.update({'current_user': self.env.user.employee_id})

    @api.depends('status')
    def _compute_can_waiting_for_approval(self):
        for claim in self:
            if claim.status == 'B':
                claim.can_waiting_for_approval = True
            else:
                claim.can_waiting_for_approval = False

    @api.depends('status')
    def _compute_can_approve(self):
        for claim in self:
            if claim.status == 'C':
                claim.can_approve = True
            else:
                claim.can_approve = False

    @api.depends('status')
    def _compute_can_reject(self):
        for claim in self:
            if claim.status == 'D':
                claim.can_reject = True
            else:
                claim.can_reject = False

    def action_confirm(self):
        res = self.write({'status': 'B'})
        return res
    def action_approve(self):
        res = self.write({'status': 'C'})
        return res
    def action_reject(self):
        res = self.write({'status': 'D'})
        return res

    @api.depends('status')
    def _get_current_user_details(self):
        for claim in self:
            if self.env.user.employee_id == claim.employee_id:
                claim.is_permission = True
            else:
                claim.is_permission = False
