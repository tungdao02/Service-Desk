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


class TimeRecorder(models.Model):
    _name = "hr.time.recorder"
    _description = "Time Recorder"

    time_recorder_id = fields.Char('Mã máy chấm công')
    address_ip = fields.Char('Địa chỉ ip')
    connection =fields.Char('Connection')
    com_port = fields.Char('Com_port')
    read_type =fields.Char('read_type')
    status=fields.Selection([('A','A'),('D','D')])
    deleted =fields.Char("deleted")
    scan_delay=fields.Char('scan_delay')
    code = fields.Char('code')
    description =fields.Char('Mô tả')
    work_address = fields.Char('Nơi làm việc')