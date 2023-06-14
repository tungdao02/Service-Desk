from odoo import api, fields, models, _


class OfficeRequest(models.Model):
    _name = 'office.request'
    _description = 'Office Request'

    office_code = fields.Char(string='Office Code')
    office_name = fields.Char(string='Office Name')
    office_unit = fields.Char(string='Office Unit')
    description = fields.Char(string='Description')
    deleted = fields.Selection([('Y', 'Chưa xóa'), ('N', 'Đã xóa')],
                              string='Trạng thái', default='Y')
