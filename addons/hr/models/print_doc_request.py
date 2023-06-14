from odoo import api, fields, models, _


class PrintDocRequest(models.Model):
    _name = 'print.doc.request'
    _description = 'print doc request'

    request_type = fields.Selection([
        ('5', 'Đơn xin văn phòng phẩm'),
        ('6', 'Đơn xin tài liệu')
    ],  tracking=True, default='6')
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True, default=lambda self: self.env.user.employee_id)
    reasons = fields.Char(string='Lý do')
    need_approve = fields.Selection([
        ('Y', 'Có'),
        ('N', 'Không')
    ],  tracking=True, default='Y')
    approver = fields.Many2one('hr.employee', default=lambda self: self.env.user.parent_id)
    depa_id = fields.Many2one('hr.department', default=lambda self: self.env.user.department_id)
    approve_type = fields.Selection([('NQL', 'Người quản lý'), ('NHD', 'Người hướng dẫn')], string='Đối tượng duyệt', default='NQL')
    request_status = fields.Selection([('A', 'Chờ HCNS duyệt'), ('B', 'Chờ phê duyệt'), ('C', 'Phê duyệt'), ('D', 'Từ chối')],
                              string='Trạng thái', default='A')
    count_print = fields.Float(string='Số lần in')
    print_doc_request_detail_ids = fields.One2many('print.doc.request.detail', 'print_doc_request_id', string='Chi tiết', copy=True)
    # parent_id = fields.Many2one('hr.employee', 'Chịu trách nhiệm', default=lambda self: self.env.user.parent_id)
    # coach_id = fields.Many2one('hr.employee', 'Coach', default=lambda self: self.env.user.coach_id)

    # @api.depends('approve_type')
    # def _compute_approved_by(self):
    #     for claim in self:
    #         manager = claim.approve_type
    #         if manager == 'NQL':
    #             claim.approver = claim.parent_id
    #         elif manager == 'NHD':
    #             claim.approver = claim.coach_id
    #         else:
    #             claim.approver = False

    def action_confirm(self):
        for claim in self:
            if claim.request_status == 'A':
                claim.request_status = 'C'

    def action_reject(self):
        for claim in self:
            if claim.request_status == 'A':
                claim.request_status = 'D'
            #  res = self.write({'request_status': 'D'})
            # else:
            #     res = self.write({'request_status': claim.request_status})
        # return res
