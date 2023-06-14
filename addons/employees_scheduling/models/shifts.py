from odoo import models, fields, api
from datetime import datetime
import calendar
from odoo.exceptions import ValidationError

today = datetime.now()
num_days_in_month = calendar.monthrange(today.year, today.month)[1]
last_day_of_month = datetime(today.year, today.month, num_days_in_month)




class Shifts(models.Model):
    _name = "shifts"
    _description = "Shifts"
    name = fields.Char('Mã ca', required=True)
    start_work_time = fields.Float('Giờ bắt đầu làm:',required=True)
    end_work_time = fields.Float('Giờ kết thúc làm:',required=True )
    start_rest_time = fields.Float('Giờ bắt đầu nghỉ:',required=True)
    end_rest_time = fields.Float('Giờ kết thúc nghỉ:',required=True)
    total_work_time = fields.Float('Tổng thời gian làm việc',  compute='_compute_total_work_time')
    total_rest_time = fields.Float('Tổng thời gian nghỉ', compute='_compute_total_rest_time')
    breakfast = fields.Boolean('Ăn sáng')
    lunch = fields.Boolean('Ăn trưa')
    dinner = fields.Boolean('Ăn tối')
    night = fields.Boolean('Đêm')
    shifts_eat = fields.Char('Ca ăn', compute='_compute_shifts_eat')
    fix_rest_time = fields.Boolean('Ca gãy', default=True, required=True)
    employees_scheduling_id = fields.Many2one('employees_scheduling', 'id')
    _sql_constraints = [('name_unique', 'UNIQUE(name)', 'Mã ca đã tồn tại!')]
    
    
    
    @api.constrains('start_work_time', 'end_work_time', 'start_rest_time', 'end_rest_time')
    def _check_time(self):
        for record in self:
            if record.start_work_time >= record.end_work_time:
                raise ValidationError("Giờ bắt đầu làm việc phải nhỏ hơn giờ kết thúc làm việc!")
            if record.start_rest_time >= record.end_rest_time:
                raise ValidationError("Giờ bắt đầu nghỉ phải nhỏ hơn giờ kết thúc nghỉ!")
            if record.start_work_time >= record.start_rest_time:
                raise ValidationError("Giờ bắt đầu làm việc phải nhỏ hơn giờ bắt đầu nghỉ!")
            if record.end_rest_time >= record.end_work_time:
                raise ValidationError("Giờ kết thúc nghỉ phải nhỏ hơn giờ kết thúc làm việc!")
            
    @api.constrains('start_work_time', 'end_work_time', 'start_rest_time', 'end_rest_time')
    def _check_time_format(self):
        for record in self:
            for time_field in ['start_work_time', 'end_work_time', 'start_rest_time', 'end_rest_time']:
                time_value = getattr(record, time_field)
                if not isinstance(time_value, float):
                    raise ValidationError(f"{time_field} phải là số thập phân!")
                hour, minute = divmod(time_value, 1)
                if not (0 <= hour < 24 and 0 <= minute < 60):
                    raise ValidationError(f"{time_field} phải ở định dạng giờ:phút và giá trị phút phải là một số nguyên từ 0 đến 59!")


    @api.depends('start_rest_time', 'end_rest_time')
    def _compute_total_rest_time(self):
        for record in self:
            record.total_rest_time = record.end_rest_time - record.start_rest_time
                
    @api.depends('start_work_time', 'end_work_time')
    def _compute_total_work_time(self):
        for record in self:
            record.total_work_time = record.end_work_time - record.start_work_time - record.total_rest_time
    
    @api.depends('breakfast', 'lunch', 'dinner', 'night')
    def _compute_shifts_eat(self):
        for record in self:
            record.shifts_eat = ''
            if record.breakfast == True:
                record.shifts_eat += 'Ăn sáng, '
            if record.lunch == True:
                record.shifts_eat += 'Ăn trưa, '
            if record.dinner == True:
                record.shifts_eat += 'Ăn tối, '
            if record.night == True:
                record.shifts_eat += 'Đêm, '
            record.shifts_eat = record.shifts_eat[:-2]
            
