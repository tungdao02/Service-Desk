from collections import defaultdict
from datetime import datetime, timedelta
from operator import itemgetter

import pytz
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
from odoo.osv.expression import AND, OR
from odoo.tools.float_utils import float_is_zero


class HrAttendanceExplanation(models.Model):
    _name = "hr.attendance.explanation"
    _description = "Attendance explanation"

    datetime_attendance = fields.Datetime('Thời gian chấm công')
    date_attendance = fields.Char(string="Ngày tạo", compute="_compute_date_time")
    time_attendance = fields.Char(string="Giờ tạo", compute="_compute_date_time")

    reason = fields.Selection([('personal','Personal'),
                               ('work','Work')],default='work',String='Reason')
    content = fields.Text('Nội dung', default=' ')
    explan_content = fields.Text('Nội dung giải trình', compute='_compute_explanation')
    status = fields.Selection([('approved', 'Đã duyệt'), ('notApproved',
                              'Chưa duyệt'), ('refused', 'Từ chối')], string='Trạng thái')

    @api.depends('reason', 'content')
    def _compute_explanation(self):
        for record in self:
            record.explan_content = record.reason + ': ' + record.content

    def action_confirm(self):
        if self.status == 'notApproved':
            self.status= 'approved'
        return True

    def action_refuse(self):
        if self.status == 'notApproved':
            self.status= 'refused'
        return True

    @api.depends('datetime_attendance')
    def _compute_date_time(self):
        # print(self)
        for record in self:
            if record.datetime_attendance:
                timezone = pytz.timezone('Asia/Ho_Chi_Minh')
                local_date = pytz.utc.localize(record.datetime_attendance).astimezone(timezone).date()
                local_time = pytz.utc.localize(record.datetime_attendance).astimezone(timezone).strftime('%H:%M')
                record.time_attendance = local_time
                record.date_attendance = local_date
            else:
                record.date_attendance = False
                record.time_attendance = False

    # @api.depends('datetime_attendance')
    # def _compute_create_time(self):
    #     for record in self:
    #         if record.datetime_attendance:
    #             timezone = pytz.timezone('Asia/Ho_Chi_Minh')
                




            #
            # timezone = pytz.timezone('Asia/Ho_Chi_Minh')
            # local_time = pytz.utc.localize(record.datetime_attendance).astimezone(timezone)
            # time1 = fields.Datetime.to_string(local_time.time())
            # print(local_time)
            # dt_str = fields.Datetime.to_string(self.datetime_attendance)
            # dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            # dt1 = datetime.strptime(local_time, "%Y-%m-%d %H:%M:%S")
            # print(dt1)
            #
            # print(record)
            # date = dt.date()
            # # time = dt.time()
            #
            # self.date_attendance =date
            # self.time_attendance = time1
        # # Trích xuất ngày và giờ
        # date = dt.date()
        # time = dt.time()
        # self.time_attendance= time
        # print(time)
        # print(self)
        # return (date, time)
        # for record in self:
        #     print(fields.Datetime.to_string(record.datetime_attendance.time()))
        #
        #     record.date_attendance = record.datetime_attendance.date()
        #     record.time_attendance = fields.Datetime.to_string(record.datetime_attendance.time())
