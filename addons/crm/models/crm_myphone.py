from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MyPhone(models.Model):
    _name = 'crm.myphone'
    _description = 'My phone calling managment'

    name = fields.Datetime(string='Lịch sử cuộc gọi',
                           required=True, default=lambda self: fields.Datetime.now())
    customer = fields.Char(string='Khách hàng',
                           required=True)
    time_spent = fields.Float(
        string='Thời lượng cuộc gọi', required=True)
    description = fields.Char(string='Mô tả')
    event_listener = fields.Char(string='Sự kiện')
    sales_team_id = fields.Many2one(
        'crm.team', string='Sale team')
    record_file = fields.Char(string='File ghi âm',
                              required=True, default='File ghi âm')
    status = fields.Selection([('đã nhận', 'Đã nhận'), ('từ chối', 'Từ chối'), (
        'khách gọi đến', 'Khách gọi đến'), ('gọi nhỡ', 'Gọi nhỡ')], default='đã nhận')

    @api.constrains('customer_phone')
    def _validate_phone(self):
        for record in self:
            if len(record.customer_phone) != 10:
                raise ValidationError('Số điện thoại không hợp lệ')
