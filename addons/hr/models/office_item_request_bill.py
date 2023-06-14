from odoo import api, fields, models, _


class OfficeItemRequestBill(models.Model):
    _name = 'office.item.request.bill'
    _description = 'Office Item Request Bill'

    request_type = fields.Selection([
        ('5', 'Đơn xin văn phòng phẩm'),
        ('6', 'Đơn xin tài liệu')
    ],  tracking=True, default='5')
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True, default=lambda self: self.env.user.employee_id)
    reasons = fields.Char(string='Lý do')
    need_approve = fields.Selection([
        ('Y', 'Có'),
        ('N', 'Không')
    ],  tracking=True, default='Y')
    approver = fields.Many2one('hr.employee', compute='_compute_approved_by', default=lambda self: self.env.user.parent_id)
    depa_id = fields.Many2one('hr.department', default=lambda self: self.env.user.department_id)
    approve_type = fields.Selection([('NQL', 'Người quản lý'), ('NHD', 'Người hướng dẫn')], string='Đối tượng duyệt', default='NQL')
    to_email = fields.Char(string='Gửi tới')
    status = fields.Selection([('A', 'Bản nháp'), ('B', 'Chờ phê duyệt'), ('C', 'Phê duyệt'), ('D', 'Từ chối')],
                              string='Trạng thái', default='A')
    office_item_bill_dtl_ids = fields.One2many('office.item.bill.dtl', 'office_item_request_id', string='Chi tiết', copy=True)

    @api.depends('approve_type')
    def _compute_approved_by(self):
        for claim in self:
            manager = claim.approve_type
            if manager == 'NQL':
                claim.approver = 1
            elif manager == 'NHD':
                claim.approver = 2
            else:
                claim.approver = False