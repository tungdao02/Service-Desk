# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	'name': "Import CRM Lead from Excel and CSV",
	'version': "16.0.0.1",
	'category': "CRM",
	'summary': "Apps helps to import Lead from excel import employee from csv, import multiple employee, import bulk employee import from excel",
	'description':	"""
					import employee  import multiple employee  import bulk employee
					import employee from excel  import employee from xls
					import employee from csv  import multiple employee from xls and csv
					""",
	'author': "QuyetHS",
	'license': 'OPL-1',
	"website" : "https://apecgroup.net",
	"price": 00,
	"currency": 'VND',
	'depends': ['base','crm'],
	'data': [
				'security/ir.model.access.csv',
				'wizard/import_lead_view.xml',
				'views/import_lead_menu.xml',
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
