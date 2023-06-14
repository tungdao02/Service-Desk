{
  'name': 'Import Scheduling',
  'description': 'Import Scheduling',
  'depends': [
    'base',
    'hr'
  ],
  'data': [
    'security/ir.model.access.csv',
    'wizard/scheduling_import_views.xml',
    'views/scheduling_import_menus.xml',
  ],
  'license': 'OPL-1',
  'application': True,
  'installable': True,
  'auto_install': True,
  "category": "Human Resources",
}