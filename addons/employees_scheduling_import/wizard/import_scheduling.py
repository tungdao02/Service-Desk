from odoo import fields, models
from odoo.exceptions import UserError, ValidationError

class ImportScheduling(models.TransientModel):
  _name = 'scheduling.import'
  _description = 'Import scheduling'

  file = fields.Binary(string='File')
  file_type = fields.Selection([('csv', 'CSV'), ('xls', 'XLS')], string='File type', default='xls')

  def action_import(self):
    if not self.file:
      raise UserError('Vui lòng chọn file để nhập dữ liệu')
    
    raise ValidationError('Tính năng đang phát triển')