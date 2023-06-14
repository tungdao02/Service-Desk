# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import datetime, timedelta
from operator import itemgetter
import csv
from odoo.exceptions import ValidationError
import pytz
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
from odoo.osv.expression import AND, OR
from odoo.tools.float_utils import float_is_zero
import datetime


class HrAttendance(models.Model):
    _name = "hr.attendance"
    _description = "Attendance"
    _order = "check_in desc"

    def _default_employee(self):
        return self.env.user.employee_id

    employee_id = fields.Many2one(
        'hr.employee', string="Employee", ondelete='cascade', index=True, readonly=False, require=True)  # , compute="_employee_code"
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
                                    readonly=True)
    company_id = fields.Many2one(
        'res.company', string="Company", related="employee_id.company_id")

    check_in = fields.Datetime(
        string="Check In")
    check_out = fields.Datetime(string="Check Out")
    worked_hours = fields.Float(
        string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)
    night_shift_hours = fields.Float(string='Night Shift Worked Hours', store=True, readonly=True)
    date_keep_time = fields.Datetime('Thời gian chấm công')
    timekeeping_date = fields.Date('Thời gian', compute="_compute_keep_date")
    timekeeping_time = fields.Char(
        'Giờ chấm công', compute="_compute_out_in")
    time_attendance = fields.Char('Lần chấm')  # ,compute="_attendance_check"
    employee_code = fields.Char(
        'Mã nhân viên', related="employee_id.code", readonly=False)
    employee_time_keeping_code = fields.Char(
        'Mã vân tay', related="employee_id.time_keeping_code", readonly=False)
    # explanation_id = fields.Many2one('hr.attendance.explanation')
    reason = fields.Selection([('personal','Personal'),
                               ('work','Work')],default='work',String='Reason', store=True)
    explanation = fields.Boolean('Giải trình', default=False, store=True)
    content = fields.Text('Nội dung', default=' ', store=True)
    content_explanation = fields.Text(
        'Đơn giải trình', compute='_compute_explanation')
    # , compute='_explanation_id'
    time_recorder_id = fields.Many2one('hr.time.recorder', 'Máy chấm công')
    data_sources = fields.Char(
        'Nguồn dữ liệu', related='time_recorder_id.address_ip')
    state = fields.Selection([('approved', 'Đã duyệt'), ('notApproved',
                              'Chưa duyệt'), ('refused', 'Từ chối')], string='Trạng thái')
    in_time = fields.Char('Giờ vào', compute="_compute_out_in")
    out_time = fields.Char('Giờ ra', compute="_compute_out_in")
    out_in = fields.Selection(
        [('out', 'Ra'), ('in', 'Vào')], string='Giờ vào/ra')

    @api.depends('explanation', 'content')
    def _compute_explanation(self):
        for record in self:
            if record.explanation and record.content:
                record.content_explanation = record.reason + ': ' + record.content
            else:
                record.content_explanation = ''
    # def action_confirm(self):
    #     if self.state == 'notApproved':
    #         self.state = 'approved'
    #     return True

    # def action_refuse(self):
    #     # for record in self:
    #     if self.state == 'notApproved':
    #         self.state= 'refuse'
    #     return True

    # @api.model
    # def write(self, vals):
    #     if vals['explanation'] and vals['content_explanation']:
    #         vals['state'] = 'notApproved'
    #         self.env['hr.attendance.explanation'].write(vals)
    #     return super().write(vals)

    @api.depends('out_in')
    def _attendance_check(self):
        print(self)
        for row in self:
            print(row)
            if row.out_in == 'in':
                print(row.time_attendance)
                if row.time_attendance == False:
                    row.time_attendance = 'check in'
            if row.out_in == 'out':
                if 'out' not in row.time_attendance:
                    row.time_attendance = 'check out'

    def create_explanation(self):
        self.explanation = True
        return {
            'name': 'Create explanation',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.attendance',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.depends('date_keep_time')
    def _compute_keep_date(self):
        # print(self)
        for record in self:
            if record.date_keep_time:
                timezone = pytz.timezone('Asia/Ho_Chi_Minh')
                local_date = pytz.utc.localize(
                    record.date_keep_time).astimezone(timezone).date()
                record.timekeeping_date = local_date
            else:
                record.timekeeping_date = False
    
    @api.depends('out_in', 'date_keep_time')
    def _compute_out_in(self):
        for record in self:
            timezone = pytz.timezone('Asia/Ho_Chi_Minh')
            local_time = pytz.utc.localize(record.date_keep_time).astimezone(
                    timezone).strftime('%H:%M')
            record.timekeeping_time = local_time
            if record.out_in == 'out':
                record.out_time = local_time
                record.in_time = ''
            else:
                record.in_time = local_time
                record.out_time = ''

            else:
                record.timekeeping_time = False
                record.timekeeping_date = False
    def name_get(self):
        result = []
        for attendance in self:
            if not attendance.check_out:
                result.append((attendance.id, _("%(empl_name)s from %(check_in)s") % {
                    'empl_name': attendance.employee_id.name,
                    'check_in': format_datetime(self.env, attendance.check_in, dt_format=False),
                }))
            else:
                result.append((attendance.id, _("%(empl_name)s from %(check_in)s to %(check_out)s") % {
                    'empl_name': attendance.employee_id.name,
                    'check_in': format_datetime(self.env, attendance.check_in, dt_format=False),
                    'check_out': format_datetime(self.env, attendance.check_out, dt_format=False),
                }))
        return result

    def get_over_lapsed_duration(self, start, end, base_start, base_end):
        result = {}
        cal_start = max(start, base_start)
        cal_end = min(end, base_end)
        result['duration'] = max(min(end, base_end) - max(start, base_start), 0)
        result['start'] = cal_start
        result['end'] = cal_end
        return result

    def time_to_int_from_midnight(self, time, is_next_day=False):
        next_day_offset = 0
        if is_next_day:
            next_day_offset = 24
        return ((time.hour + next_day_offset) * 3600 + time.minute * 60 + time.second) / 3600

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                timezone = pytz.timezone(self.env.user.tz)
                check_in = pytz.utc.localize(attendance.check_in).astimezone(timezone)
                check_out = pytz.utc.localize(attendance.check_out).astimezone(timezone)
                shifts_in_line = []
                shifts = attendance.employee_id.get_employee_shifts(check_in)
                start_night_shift = attendance.employee_id.company_id.start_night_shift
                end_night_shift = attendance.employee_id.company_id.end_night_shift
                for shift in shifts:
                    shifts_in_line.append((shift.start_work_time, shift.start_rest_time))
                    shifts_in_line.append((shift.end_rest_time, shift.end_work_time))

                start = attendance.time_to_int_from_midnight(check_in.time())
                end = start

                if check_in.date() == check_out.date():
                    end = attendance.time_to_int_from_midnight(check_out)
                else:
                    end = attendance.time_to_int_from_midnight(check_out, True)
                    shifts = attendance.employee_id.get_employee_shifts(check_out)
                    for shift in shifts:
                        shifts_in_line.append((shift.start_work_time + 24, shift.start_rest_time + 24))
                        shifts_in_line.append((shift.end_rest_time + 24, shift.end_work_time + 24))
                work_time = 0
                night_work_time = 0
                for line in shifts_in_line:
                    result = attendance.get_over_lapsed_duration(start, end, line[0], line[1])
                    work_time += result['duration']
                    if start_night_shift > end_night_shift:
                        result = attendance.get_over_lapsed_duration(result['start'], result['end'],
                                                                     0, end_night_shift)
                        result += attendance.get_over_lapsed_duration(result['start'], result['end'],
                                                                      start_night_shift, end_night_shift + 24)
                    else:
                        result = attendance.get_over_lapsed_duration(result['start'], result['end'],
                                                                     start_night_shift, end_night_shift)
                    night_work_time += result['duration']
                attendance.worked_hours = work_time
                attendance.night_shift_hours = night_work_time
            else:
                # employee = self.employee_id
                # hour = date_time_data.hour
                # shifts = employee.get_shifts(date_time_data)
                # calculate_time_dif = 24
                # nearest_shift = {}
                # for shift in shifts:
                #     cur = shift.start_work_time - hour
                #     if cur > 0 & cur < calculate_time_dif:
                #         calculate_time_dif = cur
                #         nearest_shift = shift
                # if nearest_shift is None:
                #     shifts = employee.get_shifts(date_time_data + timedelta(days=1))
                #     cur = shift.start_work_time - hour
                #     if cur > 0 & cur < calculate_time_dif:
                #         calculate_time_dif = cur
                #         nearest_shift = shift
                attendance.worked_hours = False

    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                if attendance.check_out < attendance.check_in:
                    raise exceptions.ValidationError(
                        _('"Check Out" time cannot be earlier than "Check In" time.'))

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        # TODO: skipping validate, logic should be implemented later.
        return
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
                raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                    'empl_name': attendance.employee_id.name,
                    'datetime': format_datetime(self.env, attendance.check_in, dt_format=False),
                })

            if not attendance.check_out:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                # if no_check_out_attendances:
                #     raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
                #         'empl_name': attendance.employee_id.name,
                #         'datetime': format_datetime(self.env, no_check_out_attendances.check_in, dt_format=False),
                #     })
            else:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_in', '<', attendance.check_out),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
                    raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                        'empl_name': attendance.employee_id.name,
                        'datetime': format_datetime(self.env, last_attendance_before_check_out.check_in, dt_format=False),
                    })

    @api.model
    def _get_day_start_and_day(self, employee, dt):
        # Returns a tuple containing the datetime in naive UTC of the employee's start of the day
        # and the date it was for that employee
        if not dt.tzinfo:
            date_employee_tz = pytz.utc.localize(dt).astimezone(
                pytz.timezone(employee._get_tz()))
        else:
            date_employee_tz = dt
        start_day_employee_tz = date_employee_tz.replace(
            hour=0, minute=0, second=0)
        return (start_day_employee_tz.astimezone(pytz.utc).replace(tzinfo=None), start_day_employee_tz.date())

    def _get_attendances_dates(self):
        attendances_emp = defaultdict(set)
        for attendance in self.filtered(lambda a: a.employee_id.company_id.hr_attendance_overtime and a.check_in):
            check_in_day_start = attendance._get_day_start_and_day(
                attendance.employee_id, attendance.check_in)
            if check_in_day_start[0] < datetime.combine(attendance.employee_id.company_id.overtime_start_date, datetime.min.time()):
                continue
            attendances_emp[attendance.employee_id].add(check_in_day_start)
            if attendance.check_out:
                check_out_day_start = attendance._get_day_start_and_day(
                    attendance.employee_id, attendance.check_out)
                attendances_emp[attendance.employee_id].add(
                    check_out_day_start)
        return attendances_emp

    def _update_overtime(self, employee_attendance_dates=None):
        if employee_attendance_dates is None:
            employee_attendance_dates = self._get_attendances_dates()

        overtime_to_unlink = self.env['hr.attendance.overtime']
        overtime_vals_list = []

        for emp, attendance_dates in employee_attendance_dates.items():
            # get_attendances_dates returns the date translated from the local timezone without tzinfo,
            # and contains all the date which we need to check for overtime
            attendance_domain = []
            for attendance_date in attendance_dates:
                attendance_domain = OR([attendance_domain, [
                    ('check_in', '>=', attendance_date[0]), (
                        'check_in', '<', attendance_date[0] + timedelta(hours=24)),
                ]])
            attendance_domain = AND(
                [[('employee_id', '=', emp.id)], attendance_domain])

            # Attendances per LOCAL day
            attendances_per_day = defaultdict(
                lambda: self.env['hr.attendance'])
            all_attendances = self.env['hr.attendance'].search(
                attendance_domain)
            for attendance in all_attendances:
                check_in_day_start = attendance._get_day_start_and_day(
                    attendance.employee_id, attendance.check_in)
                attendances_per_day[check_in_day_start[1]] += attendance

            # As _attendance_intervals_batch and _leave_intervals_batch both take localized dates we need to localize those date
            start = pytz.utc.localize(
                min(attendance_dates, key=itemgetter(0))[0])
            stop = pytz.utc.localize(max(attendance_dates, key=itemgetter(0))[
                                     0] + timedelta(hours=24))

            # Retrieve expected attendance intervals
            expected_attendances = emp.resource_calendar_id._attendance_intervals_batch(
                start, stop, emp.resource_id
            )[emp.resource_id.id]
            # Substract Global Leaves and Employee's Leaves
            leave_intervals = emp.resource_calendar_id._leave_intervals_batch(
                start, stop, emp.resource_id, domain=[])
            expected_attendances -= leave_intervals[False] | leave_intervals[emp.resource_id.id]

            # working_times = {date: [(start, stop)]}
            working_times = defaultdict(lambda: [])
            for expected_attendance in expected_attendances:
                # Exclude resource.calendar.attendance
                working_times[expected_attendance[0].date()].append(
                    expected_attendance[:2])

            overtimes = self.env['hr.attendance.overtime'].sudo().search([
                ('employee_id', '=', emp.id),
                ('date', 'in', [day_data[1] for day_data in attendance_dates]),
                ('adjustment', '=', False),
            ])

            company_threshold = emp.company_id.overtime_company_threshold / 60.0
            employee_threshold = emp.company_id.overtime_employee_threshold / 60.0

            for day_data in attendance_dates:
                attendance_date = day_data[1]
                attendances = attendances_per_day.get(
                    attendance_date, self.browse())
                unfinished_shifts = attendances.filtered(
                    lambda a: not a.check_out)
                overtime_duration = 0
                overtime_duration_real = 0
                # Overtime is not counted if any shift is not closed or if there are no attendances for that day,
                # this could happen when deleting attendances.
                if not unfinished_shifts and attendances:
                    # The employee usually doesn't work on that day
                    if not working_times[attendance_date]:
                        # User does not have any resource_calendar_attendance for that day (week-end for example)
                        overtime_duration = sum(
                            attendances.mapped('worked_hours'))
                        overtime_duration_real = overtime_duration
                    # The employee usually work on that day
                    else:
                        # Compute start and end time for that day
                        planned_start_dt, planned_end_dt = False, False
                        planned_work_duration = 0
                        for calendar_attendance in working_times[attendance_date]:
                            planned_start_dt = min(
                                planned_start_dt, calendar_attendance[0]) if planned_start_dt else calendar_attendance[0]
                            planned_end_dt = max(
                                planned_end_dt, calendar_attendance[1]) if planned_end_dt else calendar_attendance[1]
                            planned_work_duration += (
                                calendar_attendance[1] - calendar_attendance[0]).total_seconds() / 3600.0
                        # Count time before, during and after 'working hours'
                        pre_work_time, work_duration, post_work_time = 0, 0, 0

                        for attendance in attendances:
                            # consider check_in as planned_start_dt if within threshold
                            # if delta_in < 0: Checked in after supposed start of the day
                            # if delta_in > 0: Checked in before supposed start of the day
                            local_check_in = pytz.utc.localize(
                                attendance.check_in)
                            delta_in = (planned_start_dt -
                                        local_check_in).total_seconds() / 3600.0

                            # Started before or after planned date within the threshold interval
                            if (delta_in > 0 and delta_in <= company_threshold) or\
                                    (delta_in < 0 and abs(delta_in) <= employee_threshold):
                                local_check_in = planned_start_dt
                            local_check_out = pytz.utc.localize(
                                attendance.check_out)

                            # same for check_out as planned_end_dt
                            delta_out = (
                                local_check_out - planned_end_dt).total_seconds() / 3600.0
                            # if delta_out < 0: Checked out before supposed start of the day
                            # if delta_out > 0: Checked out after supposed start of the day

                            # Finised before or after planned date within the threshold interval
                            if (delta_out > 0 and delta_out <= company_threshold) or\
                                    (delta_out < 0 and abs(delta_out) <= employee_threshold):
                                local_check_out = planned_end_dt

                            # There is an overtime at the start of the day
                            if local_check_in < planned_start_dt:
                                pre_work_time += (min(planned_start_dt, local_check_out) -
                                                  local_check_in).total_seconds() / 3600.0
                            # Interval inside the working hours -> Considered as working time
                            if local_check_in <= planned_end_dt and local_check_out >= planned_start_dt:
                                work_duration += (min(planned_end_dt, local_check_out) - max(
                                    planned_start_dt, local_check_in)).total_seconds() / 3600.0
                            # There is an overtime at the end of the day
                            if local_check_out > planned_end_dt:
                                post_work_time += (local_check_out - max(
                                    planned_end_dt, local_check_in)).total_seconds() / 3600.0

                        # Overtime within the planned work hours + overtime before/after work hours is > company threshold
                        overtime_duration = work_duration - planned_work_duration
                        if pre_work_time > company_threshold:
                            overtime_duration += pre_work_time
                        if post_work_time > company_threshold:
                            overtime_duration += post_work_time
                        # Global overtime including the thresholds
                        overtime_duration_real = sum(attendances.mapped(
                            'worked_hours')) - planned_work_duration

                overtime = overtimes.filtered(
                    lambda o: o.date == attendance_date)
                if not float_is_zero(overtime_duration, 2) or unfinished_shifts:
                    # Do not create if any attendance doesn't have a check_out, update if exists
                    if unfinished_shifts:
                        overtime_duration = 0
                    if not overtime and overtime_duration:
                        overtime_vals_list.append({
                            'employee_id': emp.id,
                            'date': attendance_date,
                            'duration': overtime_duration,
                            'duration_real': overtime_duration_real,
                        })
                    elif overtime:
                        overtime.sudo().write({
                            'duration': overtime_duration,
                            'duration_real': overtime_duration
                        })
                elif overtime:
                    overtime_to_unlink |= overtime
        self.env['hr.attendance.overtime'].sudo().create(overtime_vals_list)
        overtime_to_unlink.sudo().unlink()

    @api.model_create_multi
    def create(self, vals_list):
        for item in vals_list:
            date_time_data = datetime.datetime.strptime(item['date_keep_time'], '%Y-%m-%d %H:%M:%S')
            if item['out_in'] == 'out':
                item['check_out'] = date_time_data
                self._cr.execute("select a.id from (select id, to_timestamp"
                                 "('" + item['date_keep_time'] + "', 'YYYY-MM-DD HH24-MI-SS')"
                                                                 "- ha.check_in as dif from hr_attendance ha "
                                                                 "where ha.check_in <= to_timestamp('" + item[
                                     'date_keep_time'] +
                                 "', 'YYYY-MM-DD HH24-MI-SS')"
                                 " and ha.check_out is null)a order by a.dif fetch first 1 rows only")
                last_check_in_id = self._cr.fetchall()
                if len(last_check_in_id) > 0:
                    last_check_in = self.env['hr.attendance'].search([('id', '=', last_check_in_id)])
                    last_check_in.check_out = date_time_data
            else:
                item['check_in'] = date_time_data

        res = super().create(vals_list)
        for rec in res:
            if rec.explanation and rec.content_explanation:
                rec.state = 'notApproved'
                self.env['hr.attendance.explanation'].create({
                    'datetime_attendance': rec.date_keep_time,
                    'reason': rec.reason,
                    'content': rec.content,
                    'status': 'notApproved',
                })
        res._update_overtime()
        return res

    def write(self, vals):
        attendances_dates = self._get_attendances_dates()
        # if vals['explanation'] and vals['content'].strip():
        #     self.env['hr.attendance.explanation'].create({
        #             'datetime_attendance': vals['date_keep_time'],
        #             'reason': vals['reason'],
        #             'content': vals['content'],
        #             'status': vals['state'],
        #         })
        super(HrAttendance, self).write(vals)
        if any(field in vals for field in ['employee_id', 'check_in', 'check_out']):
            # Merge attendance dates before and after write to recompute the
            # overtime if the attendances have been moved to another day
            for emp, dates in self._get_attendances_dates().items():
                attendances_dates[emp] |= dates
            self._update_overtime(attendances_dates)

    def unlink(self):
        attendances_dates = self._get_attendances_dates()
        super(HrAttendance, self).unlink()
        self._update_overtime(attendances_dates)

    @api.returns('self', lambda value: value.id)
    def copy(self):
        raise exceptions.UserError(_('You cannot duplicate an attendance.'))

    # @api.depends('explanation_id')
    # def _explanation_id(self):
    #     for i in self:
    #         print('==================',i)
    #         print('--------------------',i.explanation_id)
    #         if i.explanation_id :
    #             print("aaaa",i.content_explanation)
    #             i.content_explanation = 'AAAAAA'
    #             print(i.content_explanation)
    #         i.content_explanation = False

        # for item in i.explanation_id:
        #     if i
        #     print('----------------------',i.content_explanation)
        #     print('========================',item.content)
        #     i.content_explanation = item.content
