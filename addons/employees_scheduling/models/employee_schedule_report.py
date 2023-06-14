from odoo import models, fields, api
from datetime import datetime, timedelta, date
import calendar

today = datetime.now()


class EmployeeScheduleReport(models.TransientModel):
    _name = "employee.schedule.report"

    month = fields.Selection(
        [
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
            ("6", "6"),
            ("7", "7"),
            ("8", "8"),
            ("9", "9"),
            ("10", "10"),
            ("11", "11"),
            ("12", "12"),
        ],
        default=str(today.month),
    )

    year = fields.Selection(
        [
            (str(today.year - 4), str(today.year - 4)),
            (str(today.year - 3), str(today.year - 3)),
            (str(today.year - 2), str(today.year - 2)),
            (str(today.year - 1), str(today.year - 1)),
            (str(today.year), str(today.year)),
            (str(today.year + 1), str(today.year + 1)),
        ],
        default=str(today.year),
    )
    selected_string = fields.Char(compute="_get_selected_string")

    def _get_selected_string(self):
        for rec in self:
            rec.selected_string = dict(self._fields.get("month").selection).get(
                rec.month
            )

    def generate_report(self):
        employees = self.env["hr.employee"].search([])
        employees_scheduling = self.env["employees_scheduling"].search(
            [("employee_ids", "!=", False)]
        )
        employee_report = self.env["employee.schedule.inherit"]
        employee_report.search([]).unlink()
        total_day = calendar.monthrange(int(self.year), int(self.month))[1]
        employees_arr = []
        for employee in employees:
            for scheduling in employees_scheduling:
                for emp in scheduling.employee_ids:
                    if (
                        emp.id == employee.id
                        and (employee.id in employees_arr) == False
                    ):
                        employees_arr.append(employee.id)
                        obj_employee = {
                            "date_of_report": self.month + "/" + self.year,
                            "employee_id": employee.id,
                            "total_day": total_day,
                            "code": employee.code,
                            "name": employee.name,
                            "department": employee.department_id.name,
                            "company": employee.company_id.name,
                        }
                        obj_employee = self.get_employee_schedule(
                            employees_scheduling,
                            int(self.year),
                            int(self.month),
                            employee.id,
                            obj_employee,
                        )
                        employee_report.create(obj_employee)
        return {
            "type": "ir.actions.act_window",
            "target": "current",
            "name": f"Danh sách phân ca",
            "view_mode": "tree",
            "view_id": self.env.ref(
                "employees_scheduling.employee_schedule_inherit_view"
            ).id,
            "context": {'group_by': ['company', 'department'], 'expand': 1},
            'expand': 1,
            "res_model": "employee.schedule.inherit",
        }

    def get_employee_schedule(
        self, employees_scheduling, year, month, employee_id, obj_employee
    ):
        employees_scheduling = self.env["employees_scheduling"].search(
            [("employee_ids", "!=", False)]
        )
        total_day = calendar.monthrange(int(year), int(month))[1]
        start_date_report = date(year, month, 1)
        end_date_report = date(year, month, total_day)
        for scheduling in employees_scheduling:
            for emp in scheduling.employee_ids:
                if emp.id == employee_id and (
                    scheduling.start <= start_date_report
                    or scheduling.stop >= end_date_report
                ):
                    obj_day = obj_employee
                    day = 1
                    while day <= total_day:
                        day_name = "day" + str(day)
                        scheduling_value = ""
                        day_report = date(year, month, day)
                        day_report_number = day_report.isoweekday()
                        if scheduling.start <= day_report and scheduling.stop >= day_report:
                            if day_report_number == 7:  # chủ nhật
                                for item in scheduling.shift_sunday:
                                    scheduling_value += f'<span class="tag_employee_schedule" title="{item.name} => bắt đầu: {item.start_work_time}, kết thúc: {item.end_work_time}" onclick="confirm_schedule({emp.id, day, month, year})"> 12' + item.name + '</span>'
                            elif day_report_number == 1:  # thứ 2
                                for item in scheduling.shift_monday:
                                    scheduling_value += f'<span class="tag_employee_schedule" title="{item.name} => bắt đầu: {item.start_work_time}, kết thúc: {item.end_work_time}">' + item.name + '</span>'
                            elif day_report_number == 2:  # thứ 3
                                for item in scheduling.shift_tuesday:
                                    scheduling_value += f'<span class="tag_employee_schedule" title="{item.name} => bắt đầu: {item.start_work_time}, kết thúc: {item.end_work_time}">' + item.name + '</span>'
                            elif day_report_number == 3:  # thứ 4
                                for item in scheduling.shift_wednesday:
                                    scheduling_value += f'<span class="tag_employee_schedule" title="{item.name} => bắt đầu: {item.start_work_time}, kết thúc: {item.end_work_time}">' + item.name + '</span>'
                            elif day_report_number == 4:  # thứ 5
                                for item in scheduling.shift_thursday:
                                    scheduling_value += f'<span class="tag_employee_schedule" title="{item.name} => bắt đầu: {item.start_work_time}, kết thúc: {item.end_work_time}">' + item.name + '</span>'
                            elif day_report_number == 5:  # thứ 6
                                for item in scheduling.shift_friday:
                                    scheduling_value += f'<span class="tag_employee_schedule" title="{item.name} => bắt đầu: {item.start_work_time}, kết thúc: {item.end_work_time}">' + item.name + '</span>'
                            elif day_report_number == 6:  # thứ 7
                                for item in scheduling.shift_saturday:
                                    scheduling_value += f'<span class="tag_employee_schedule" title="{item.name} => bắt đầu: {item.start_work_time}, kết thúc: {item.end_work_time}">' + item.name + '</span>'
                            obj_day[day_name] = scheduling_value
                        day += 1
                    return obj_day


class EmployeeScheduleInherit(models.TransientModel):
    _name = "employee.schedule.inherit"
    _description = "Employee inherit"
    _order = "name"

    employee_schedule_report_id = fields.Many2one(
        "employee.schedule.report", ondelete="cascade"
    )
    selected_month = fields.Char(
        related="employee_schedule_report_id.selected_string",
        string="Tháng",
        readonly=True,
    )
    
    date_of_report = fields.Char("Tháng TH")
    employee_id = fields.Integer("Id của nhân viên")
    name = fields.Char(string="Tên nhân viên")
    code = fields.Char(string="Mã nhân viên")
    department = fields.Char(string="Phòng ban")
    company = fields.Char(string="Công ty")
    total_day = fields.Float("Tổng ngày của tháng", default="3")

    day1 = fields.Char(string="01")
    colorDay1 = fields.Integer(compute="_compute_color", default=1)
    invisibleDay1 = fields.Boolean("Hiển thị", required=False, default=True)

    day2 = fields.Char(string="02", required=False)
    colorDay2 = fields.Integer("Màu ngày", default=1)
    invisibleDay2 = fields.Boolean("Hiển thị", required=False)

    day3 = fields.Char(string="03", required=False)
    colorDay3 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay3 = fields.Boolean("Hiển thị", required=False)

    day4 = fields.Char(string="04", required=False)
    colorDay4 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay4 = fields.Boolean("Hiển thị", required=False)

    day5 = fields.Char(string="05", required=False)
    colorDay5 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay5 = fields.Boolean("Hiển thị", required=False)

    day6 = fields.Char(string="06", required=False)
    colorDay6 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay6 = fields.Boolean("Hiển thị", required=False)

    day7 = fields.Char(string="07", required=False)
    colorDay7 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay7 = fields.Boolean("Hiển thị", required=False)

    day8 = fields.Char(string="08", required=False)
    colorDay8 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay8 = fields.Boolean("Hiển thị", required=False)

    day9 = fields.Char(string="09", required=False)
    colorDay9 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay9 = fields.Boolean("Hiển thị", required=False)

    day10 = fields.Char(string="10", required=False)
    colorDay10 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay10 = fields.Boolean("Hiển thị", required=False)

    day11 = fields.Char(string="11", required=False)
    colorDay11 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay11 = fields.Boolean("Hiển thị", required=False)

    day12 = fields.Char(string="12", required=False)
    colorDay12 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay12 = fields.Boolean("Hiển thị", required=False)

    day13 = fields.Char(string="13", required=False)
    colorDay13 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay13 = fields.Boolean("Hiển thị", required=False)

    day14 = fields.Char(string="14", required=False)
    colorDay14 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay14 = fields.Boolean("Hiển thị", required=False)

    day15 = fields.Char(string="15", required=False)
    colorDay15 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay15 = fields.Boolean("Hiển thị", required=False)

    day16 = fields.Char(string="16", required=False)
    colorDay16 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay16 = fields.Boolean("Hiển thị", required=False)

    day17 = fields.Char(string="17", required=False)
    colorDay17 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay17 = fields.Boolean("Hiển thị", required=False)

    day18 = fields.Char(string="18", required=False)
    colorDay18 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay18 = fields.Boolean("Hiển thị", required=False)

    day19 = fields.Char(string="19", required=False)
    colorDay19 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay19 = fields.Boolean("Hiển thị", required=False)

    day20 = fields.Char(string="20", required=False)
    colorDay20 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay20 = fields.Boolean("Hiển thị", required=False)

    day21 = fields.Char(string="21", required=False)
    colorDay21 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay21 = fields.Boolean("Hiển thị", required=False)

    day22 = fields.Char(string="22", required=False)
    colorDay22 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay22 = fields.Boolean("Hiển thị", required=False)

    day23 = fields.Char(string="23", required=False)
    colorDay23 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay23 = fields.Boolean("Hiển thị", required=False)

    day24 = fields.Char(string="24", required=False)
    colorDay24 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay24 = fields.Boolean("Hiển thị", required=False)

    day25 = fields.Char(string="25", required=False)
    colorDay25 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay25 = fields.Boolean("Hiển thị", required=False)

    day26 = fields.Char(string="26", required=False)
    colorDay26 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay26 = fields.Boolean("Hiển thị", required=False)

    day27 = fields.Char(string="27", required=False)
    colorDay27 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay27 = fields.Boolean("Hiển thị", required=False)

    day28 = fields.Char(string="28", required=False)
    colorDay28 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay28 = fields.Boolean("Hiển thị", required=False)

    day29 = fields.Char(string="29", required=False)
    colorDay29 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay29 = fields.Boolean("Hiển thị", required=False)

    day30 = fields.Char(string="30", required=False)
    colorDay30 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay30 = fields.Boolean("Hiển thị", required=False)

    day31 = fields.Char(string="31", required=False)
    colorDay31 = fields.Integer("Màu ngày", required=False, default=1)
    invisibleDay31 = fields.Boolean("Hiển thị", required=False)

    # @api.depends('month_of_year')
    # def _compute_employees_scheduling(self):
    #     if not self.employees_scheduling_ids:
    #         self.total_scheduling = 0
    #     else:
    #         self.total_scheduling = len(self.employees_scheduling_ids)
    #
    # @api.depends('day01')
    # def _compute_color(self):
    #     for update in self:
    #         update.colorDay01 = 1
    #
    # def _compute_month_of_year(self):
    #     return self
    #
    # @api.depends("month_of_year")
    # def _compute_day(self):
    #     for item in self:
    #         item.day01 = 'Ca 01'
    #     return self
