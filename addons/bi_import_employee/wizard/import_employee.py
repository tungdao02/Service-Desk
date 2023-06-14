# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import io
import xlrd
import babel
import logging
import tempfile
import binascii
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


class ImportEmployee(models.TransientModel):
	_name = 'import.employee'
	_description = 'Import Employee'

	file_type = fields.Selection([('CSV', 'CSV File'),('XLS', 'XLS File')],string='File Type', default='CSV')
	file = fields.Binary(string="Upload File")

	def import_employee(self):
		if not self.file:
			raise ValidationError(_("Please Upload File to Import Employee !"))

		if self.file_type == 'CSV':
			line = keys = ['code', 'time_keeping_code', 'name', 'work_email', 'job_title','parent_id',
						   'mobile_phone','department_id','company_id']
			# line = keys = ['code','time_keeping_code','name','job_title','mobile_phone','work_phone','work_email','department_id','address_id','gender','birthday']
			try:
				csv_data = base64.b64decode(self.file)
				data_file = io.StringIO(csv_data.decode("utf-8"))
				data_file.seek(0)
				file_reader = []
				csv_reader = csv.reader(data_file, delimiter=',')
				file_reader.extend(csv_reader)
			except Exception:
				raise ValidationError(_("Please Select Valid File Format !"))
				
			values = {}
			for i in range(len(file_reader)):
				field = list(map(str, file_reader[i]))
				values = dict(zip(keys, field))
				if values:
					if i == 0:
						continue
					else:
						res = self.create_employee(values)
		else:
			try:
				file = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
				file.write(binascii.a2b_base64(self.file))
				file.seek(0)
				values = {}
				workbook = xlrd.open_workbook(file.name)
				sheet = workbook.sheet_by_index(0)
			except Exception:
				raise ValidationError(_("Please Select Valid File Format !"))

			for row_no in range(sheet.nrows):
				val = {}
				if row_no <= 0:
					fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
				else:
					line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
					values.update({
						    'code':line[0],
						    'time_keeping_code': line[1],
						    'name': line[2],
						    'work_email':line[3],
						    'job_title':line[4],
						    'parent_id':line[5],
						    'mobile_phone':line[6],
						    'department_id':line[7],
						    'company_id':line[8],
							# 'name':line[0],
							# 'job_title': line[1],
							# 'mobile_phone': line[2],
							# 'work_phone':line[3],
							# 'work_email':line[4],
							# 'department_id':line[5],
							# 'address_id':line[6],
							# 'gender':line[7],
							# 'birthday':line[8],
							})
					res = self.create_employee(values)


	def create_employee(self, values):
		employee = self.env['hr.employee']
		department_id = self.get_department(values.get('department_id'))

		if not values.get('parent_id'):
			parent_id = self.get_parent(values.get('parent_id'))

		parent = parent_id.id
		# parent_id = self.get_parent(values.get('parent_id'))
		# address_id = self.get_address(values.get('address_id'))
		# birthday = self.get_birthday(values.get('birthday'))
		
		if values.get('gender') == 'Male':
			gender ='male'
		elif values.get('gender') == 'male':
			gender ='male'
		elif values.get('gender') == 'Female':
			gender ='female'
		elif values.get('gender') == 'female':
			gender ='female'
		elif values.get('gender') == 'Other':
			gender ='other'
		else:
			gender = 'male'
		
		vals = {
			'code': values.get('code'),
			'time_keeping_code': values.get('time_keeping_code'),
			'name': values.get('name'),
			'work_email': values.get('work_email'),
			'job_title': values.get('job_title'),
			'parent_id': parent,
			'mobile_phone': values.get('mobile_phone'),
			'department_id': department_id.id,
				# 'name' : values.get('name'),
				# 'job_title' : values.get('job_title'),
				# 'mobile_phone' : values.get('mobile_phone'),
				# 'work_phone' : values.get('work_phone'),
				# 'work_email' : values.get('work_email'),
				# 'department_id' : department_id.id,
				# 'address_id' : address_id.id,
				# 'gender' : gender,
				# 'birthday' : birthday,
				}


		if values.get('name')=='':
			raise UserError(_('Employee Name is Required !'))
		if values.get('department_id')=='':
			raise UserError(_('Department Field can not be Empty !'))

		# if values.get('parent_id')=='':
		# 	raise UserError(_('Parent Field can not be Empty !'))

		res = employee.create(vals)
		return res


	def get_department(self, name):
		department = self.env['hr.department'].search([('name', '=', name)],limit=1)
		if department:
			return department
		else:
			raise UserError(_('"%s" Department is not found in system !') % name)

	def get_parent(self, name):
		parent = self.env['hr.employee'].search([('name', '=', name)], limit=1)
		return parent
		# if parent:
		#
		# else:
		# 	raise UserError(_('"%s" Parent is not found in system !') % name)

	def get_company(self, name, department_name):
		company = self.env['res.company'].search([('name', '=', name)], limit=1)
		if company:
			department = self.env['hr.department'].search([('name', '=', department_name),('company_id', '=', company.id)], limit=1)
			if department:
				return company
			else:
				raise UserError(_('"%s" Phòng ban không thuộc khách sạn !') % department_name)
		else:
			raise UserError(_('"%s" Parent is not found in system !') % name)

	def get_address(self, name):
		address = self.env['res.partner'].search([('name', '=', name)],limit=1)
		if address:
			return address
		else:
			raise UserError(_('"%s" Address is not found in system !') % name)

	def get_birthday(self, date):
		try:
			birthday = datetime.strptime(date, '%Y/%m/%d')
			return birthday
		except Exception:
			raise ValidationError(_('Wrong Date Format ! Date Should be in format YYYY/MM/DD'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: