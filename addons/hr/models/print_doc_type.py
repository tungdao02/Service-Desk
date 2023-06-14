from odoo import api, fields, models, _


class PrintDocType(models.Model):
    _name = 'print.doc.type'
    _description = 'Print Doc Type'

    print_doc_type = fields.Char(string='Mã')
    print_doc_name = fields.Char(string='Tên')
    deleted = fields.Selection([('Y', 'Chưa xóa'), ('N', 'Đã xóa')],
                              string='Trạng thái', default='Y')
