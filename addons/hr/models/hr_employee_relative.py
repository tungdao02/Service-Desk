import base64
from pytz import UTC
from datetime import datetime, time
from random import choice
from string import digits
from werkzeug.urls import url_encode
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError
from odoo.osv import expression
from odoo.tools import format_date, Query


class EmployeeRelative(models.Model):
    _name = "hr.employee.relative"
    _description = "EmployeeRelative"

    name = fields.Char(string="Họ tên", tracking=True)
    birthday = fields.Date('Ngày sinh', tracking=True)
    phone = fields.Date('Số điện thoại', tracking=True)
    relationship = fields.Selection([
        ('dad', 'Bố'),
        ('mother', 'Mẹ'),
        ('other', 'Other'),
    ], 'Quan hệ', default='other', tracking=True)
    family_allowances = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], 'Giảm trừ gia cảnh', default='no', tracking=True)
    job = fields.Char(string="Nghề nghiệp", tracking=True)
    note = fields.Char(string="Ghi chú", tracking=True)
    employee_id = fields.Many2one('hr.employee', required=True, default=lambda self: self.env.user.employee_id)