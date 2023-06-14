from odoo import api, fields, models, _


class PrintDocUnit(models.Model):
    _name = 'print.doc.unit'
    _description = 'Print Doc Unit'

    unit = fields.Char(string='Tên')
    deleted = fields.Selection([('Y', 'Chưa xóa'), ('N', 'Đã xóa')],
                              string='Trạng thái', default='Y')
