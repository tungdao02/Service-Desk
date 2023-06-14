# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	'name': "Import Employee from Excel and CSV",
	'version': "16.0.0.1",
	'category': "Employees",
	'summary': "Apps helps to import employee from excel import employee from csv, import multiple employee, import bulk employee import from excel",
	'description':	"""
					import employee  import multiple employee  import bulk employee
					import employee from excel  import employee from xls
					import employee from csv  import multiple employee from xls and csv
					""",
	'author': "BrowseInfo",
	'license': 'OPL-1',
	"website" : "https://www.browseinfo.in",
	"price": 00,
	"currency": 'EUR',
	'depends': ['base','hr'],
	'data': [
				'security/ir.model.access.csv',
				'wizard/import_employee_view.xml',
				'views/import_employee_menu.xml',
			],
	'demo': [],
	'qweb': [],
	'installable': True,
	'auto_install': True,
	'application': True,
	"live_test_url":'https://youtu.be/oqlqPMfwWo0',
	"images":['static/description/Banner.gif'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
