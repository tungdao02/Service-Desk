# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import io
import chardet
import pytz
import xlrd
import babel
import logging
import tempfile
import binascii
import pandas as pd
import json
from io import StringIO
from datetime import date, datetime, time
from odoo import api, fields, models, tools, _
from odoo.exceptions import Warning, UserError, ValidationError

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class ImportAttendance(models.TransientModel):
    _name = 'import.attendance'
    _description = 'Import Attendance'

    file_type = fields.Selection(
        [('CSV', 'CSV File'), ('XLSX', 'XLSX File')], string='File Type', default='XLSX')
    file = fields.Binary(string="Upload File")

    def import_attendance(self):
        if not self.file:
            raise ValidationError(_("Please Upload File to Import !"))

        Employee = self.env['hr.employee']
        Attendance = self.env['hr.attendance']
        Time_recorder = self.env['hr.time.recorder']
        _file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        _file.write(binascii.a2b_base64(self.file))
        _file.seek(0)
        vals_list = []

        if self.file_type == 'CSV':
            # csv_obj = open(_file.name, 'rb')
            # heading = next(csv_obj)
            # data_obj = csv.reader(csv_obj)
            try:
                with open(_file.name, 'rb') as f:
                    enc = chardet.detect(f.read())

                df = pd.read_csv(_file.name, encoding = enc['encoding'])
                col_0 = df.columns[0]
                col_1 = df.columns[1]
                col_2 = df.columns[2]
                col_3 = df.columns[3]
                # print(col_0, col_1, col_2, col_3)
                for i, row in df.iterrows():
                    if row[col_0] and row[col_1] and row[col_2] and row[col_3]:
                        
                        # check employee available with time_keeping_code property
                        employee = Employee.search(
                            [('time_keeping_code', '=', row[col_0])], limit=1)
                        if not employee:
                            raise UserError(f'Mã chấm công {row[col_0]} không tồn tại')
                            # continue
                        else:
                            print(row[col_0],row[col_1],row[col_2],row[col_3])

                        # Check if Time-recorder exist
                        time_recorder = Time_recorder.search(
                            [('time_recorder_id', '=', row[col_3])], limit=1)
                        if not time_recorder:
                            raise UserError(f'Mã máy chấm công {row[col_3]} không tồn tại')
                        
                        local_time = datetime.strptime(row[col_1], "%d/%m/%Y %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')
                        vals_list.append({
                            'employee_id': employee.id,
                            'date_keep_time': local_time,
                            'out_in': 'out' if 'out' in row[2] else 'in',
                            # 'time_recorder_id': time_recorder.id,
                        })
                    else:
                        raise UserError('Some fields are INVALID')

                # Create attendance records
            except Exception as e:
                raise UserError(e)
        else:
            try:
                try:
                    workbook = xlrd.open_workbook(_file.name)
                    worksheet = workbook.sheet_by_index(0)
                    print('worksheet ', worksheet)
                except Exception:
                    raise ValidationError(_("Please Select Valid File Format !"))
                
                for i in range(1, worksheet.nrows):
                    rec = [str(cell.value).strip() for cell in worksheet.row(i)]                
                    if rec[0] and rec[1] and rec[2] and rec[3]:
                        
                        # check employee available with time_keeping_code property
                        employee = Employee.search(
                            [('time_keeping_code', '=', rec[0].split('.')[0])], limit=1)
                        if not employee:
                            raise UserError(f"Mã chấm công {rec[0].split('.')[0]} không tồn tại")
                            # continue
                        else:
                            print(rec[0], rec[1], rec[2], rec[3])

                        # Check if Time-recorder exist
                        time_recorder = Time_recorder.search(
                            [('time_recorder_id', '=', rec[3].split('.')[0])], limit=1)
                        if not time_recorder:
                            raise UserError(f"Mã máy chấm công {rec[3].split('.')[0]} không tồn tại")
                            # continue

                        local_time = datetime.strptime(rec[1], "%d/%m/%Y %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')
                        vals_list.append({
                            'employee_id': employee.id,
                            'date_keep_time': local_time,
                            'out_in': 'out' if 'out' in rec[2] else 'in',
                            # 'time_recorder_id': time_recorder.id
                        })
            except Exception as e:
                raise UserError(e)

        Attendance.create(vals_list)
        return {
            'name' : 'Attendances',
            'view_type' : 'tree',
            'view_mode' : 'tree,form',
            'view_id': False,
            'res_model' : 'hr.attendance',
            'type' : 'ir.actions.act_window',
            'target' : 'current',
        }
