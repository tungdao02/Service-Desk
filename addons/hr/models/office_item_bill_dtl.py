from odoo import api, fields, models, _


class OfficeItemBillDtl(models.Model):
    _name = 'office.item.bill.dtl'
    _description = 'Office Item Bill Dtl'

    office_item_request_id = fields.Many2one('office.item.request.bill', required=True)
    office_request_id = fields.Many2one('office.request', required=True)
    office_name = fields.Char(string='Tên', related='office_request_id.office_name')
    office_unit = fields.Char(string='Đơn vị tính', related='office_request_id.office_unit')
    description = fields.Char(string='Description')
    quantity = fields.Float(string='Số lượng')
    receiver = fields.Many2one('hr.employee')
    real_quantity = fields.Float(string='Số lượng được duyệt')
