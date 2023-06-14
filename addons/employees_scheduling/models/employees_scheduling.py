from odoo import models, fields, api
from datetime import datetime
import calendar

from odoo.exceptions import UserError, ValidationError

today = datetime.now()
num_days_in_month = calendar.monthrange(today.year, today.month)[1]
last_day_of_month = datetime(today.year, today.month, num_days_in_month)


class EmployeeInherit(models.Model):
    _inherit = "hr.employee"
    employees_scheduling_ids = fields.Many2many(
        "employees_scheduling", "scheduling_id", required=True
    )

    @api.model
    def get_employee_shifts(self, date_selected):
        shifts_day = []

        d_o_w = date_selected.weekday()
        for schedule in self.employees_scheduling_ids:
            if d_o_w == 0:
                for shift in schedule.shift_monday:
                    shifts_day.append(shift)
            elif d_o_w == 1:
                for shift in schedule.shift_tuesday:
                    shifts_day.append(shift)
            elif d_o_w == 2:
                for shift in schedule.shift_wednesday:
                    shifts_day.append(shift)
            elif d_o_w == 3:
                for shift in schedule.shift_thursday:
                    shifts_day.append(shift)
            elif d_o_w == 4:
                for shift in schedule.shift_friday:
                    shifts_day.append(shift)
            elif d_o_w == 5:
                for shift in schedule.shift_saturday:
                    shifts_day.append(shift)
            elif d_o_w == 6:
                for shift in schedule.shift_sunday:
                    shifts_day.append(shift)
        return shift


class employees_Scheduling_Model(models.Model):
    _name = "employees_scheduling"
    _description = "Employees Scheduling"
    start = fields.Date(
        "From date", required=True, default=datetime(today.year, today.month, 1)
    )
    stop = fields.Date("To date", default=last_day_of_month, required=True)
    shift_monday = fields.Many2many(
        "shifts", "employees_scheduling_id", required=True, string="Thứ 2"
    )
    shift_tuesday = fields.Many2many(
        "shifts", "employees_scheduling_id_2", required=True, string="Thứ 3"
    )
    shift_wednesday = fields.Many2many(
        "shifts", "employees_scheduling_id_3", required=True, string="Thứ 4"
    )
    shift_thursday = fields.Many2many(
        "shifts", "employees_scheduling_id_4", required=True, string="Thứ 5"
    )
    shift_friday = fields.Many2many(
        "shifts", "employees_scheduling_id_5", required=True, string="Thứ 6"
    )
    shift_saturday = fields.Many2many(
        "shifts", "employees_scheduling_id_6", required=True, string="Thứ 7"
    )
    shift_sunday = fields.Many2many(
        "shifts", "employees_scheduling_id_7", required=True, string="Chủ nhật"
    )
    employee_ids = fields.Many2many("hr.employee", "scheduling_id", required=True)
   

    @api.constrains("stop")
    def _check_dates(self):
        for rec in self:
            if rec.start and rec.stop and rec.stop < rec.start:
                raise ValidationError("To date must be after From date!")
            

    @api.constrains("employee_ids","start", "stop")
    def check_overlap_shifts(self):
        for rec in self:
            if rec.start and rec.stop:
                overlap_schedules = self.search([
                    ("id", "!=", rec.id),
                    ("employee_ids", "in", rec.employee_ids.ids),
                    "|",
                    "&", ("start", "<=", rec.start), ("stop", ">=", rec.start),
                    "&", ("start", "<=", rec.stop), ("stop", ">=", rec.stop),
                ])   
            for employee in rec.employee_ids:
                for day in range(1, 8):
                    if day == 1:
                        shifts = employee.employees_scheduling_ids.shift_monday
                    elif day == 2:
                        shifts = employee.employees_scheduling_ids.shift_tuesday
                    elif day == 3:
                        shifts = employee.employees_scheduling_ids.shift_wednesday
                    elif day == 4:
                        shifts = employee.employees_scheduling_ids.shift_thursday
                    elif day == 5:
                        shifts = employee.employees_scheduling_ids.shift_friday
                    elif day == 6:
                        shifts = employee.employees_scheduling_ids.shift_saturday
                    elif day == 7:
                        shifts = employee.employees_scheduling_ids.shift_sunday
                    for shift in shifts:
                        for shift2 in shifts:
                            if shift != shift2:
                                if overlap_schedules:
                                    if (
                                    
                                        shift.start_work_time
                                        < shift2.start_work_time
                                        < shift.end_work_time
                                    ):
                                        raise ValidationError(
                                            "There are overlapping shifts in the same day!"
                                    )
                                    elif (
                                        shift.start_work_time
                                        < shift2.end_work_time
                                        < shift.end_work_time
                                    ):
                                        raise ValidationError(
                                            "There are overlapping shifts in the same day!"
                                        )
                                    elif (
                                        shift2.start_work_time
                                        < shift.start_work_time
                                        < shift2.end_work_time
                                    ):
                                        raise ValidationError(
                                            "There are overlapping shifts in the same day!"
                                        )
                                    elif (
                                        shift2.start_work_time
                                        < shift.end_work_time
                                        < shift2.end_work_time
                                    ):
                                        raise ValidationError(
                                            "There are overlapping shifts in the same day!"
                                        )
