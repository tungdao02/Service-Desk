from odoo import api, fields, models, _


class PrintDocRequestDetail(models.Model):
    _name = 'print.doc.request.detail'
    _description = 'Print Doc Request Detail'

    doc_name = fields.Char(string='Tên', required=True)
    print_doc_request_id = fields.Many2one('print.doc.request', required=True)
    print_doc_category_id = fields.Many2one('print.doc.category', required=True)
    unit = fields.Many2one('print.doc.unit', required=True)
    unit_price = fields.Float(string='Số lượng')
    description = fields.Char(string='Mô tả')
    quantity = fields.Float(string='Số lượng')
    content = fields.Char(string='Nội dung')
    note = fields.Char(string='Ghi chú')
