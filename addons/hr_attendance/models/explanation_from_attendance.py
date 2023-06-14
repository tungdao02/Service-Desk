from odoo import fields, models

class ExplanationFromAttendance(models.Model):
  _inherit = 'hr.attendance'

  def action_approve(self):
    if self.state == 'notApproved':
      self.state = 'approved'
    return

  def action_refuse(self):
    if self.state == 'notApproved':
      self.state = 'refused'
    return