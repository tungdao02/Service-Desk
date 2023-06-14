from odoo import api, fields, models, _


class PrintDocCategory(models.Model):
    _name = 'print.doc.category'
    _description = 'Print Doc Category'

    print_doc_code = fields.Char(string='Mã')
    print_doc_name = fields.Char(string='Tên')
    print_doc_type = fields.Many2one('print.doc.type')
    unit = fields.Many2one('print.doc.unit')
    unit_price = fields.Float(string='Đơn giá')
    deleted = fields.Selection([('Y', 'Chưa xóa'), ('N', 'Đã xóa')],
                              string='Trạng thái', default='Y')
