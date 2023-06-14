# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import io
import xlrd
import babel
import logging
import tempfile
import binascii
import json
from io import StringIO
from datetime import date, datetime, time
from odoo import api, fields, models, tools, _
from odoo.exceptions import Warning, UserError, ValidationError
from datetime import date

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


class ImportLead(models.TransientModel):
    _name = 'import.lead'
    _description = 'Import Lead'

    file_type = fields.Selection([('CSV', 'CSV File'), ('XLS', 'XLS File')], string='File Type', default='CSV')
    file = fields.Binary(string="Upload File")
    duplicated_count = fields.Integer("Duplicate Count", default=0)
    inserted_count = fields.Integer("Inserted Count", default=0)
    overriding_old_data = fields.Boolean("Renew by the duplicate")
    duplicate_data_ref_ids = fields.One2many('import.raw.data', 'import_lead_id',
                                             string='Duplicate Data',
                                             domain=lambda self: [('duplicated', '=', True)])
    inserted_data_ref_ids = fields.One2many('import.raw.data', 'import_lead_id',
                                            string='Duplicate Data',
                                            domain=lambda self: [('duplicated', '=', False)])
    import_target_storage = fields.Many2one(comodel_name='crm.lead.storage.ref.info',
                                            required=True, string='Import Target')
    filter_duplicated = fields.Many2many('ir.model.fields', 'import_lead_rel', 'import_id', 'field_id',
                                         string='Filter Duplicate',
                                         domain="[('model', '=', 'import.raw.data')]")
    # filter_duplicated_ids = fields.Many2one('ir.model.fields', string='Filter Duplicate',
    #                                         domain="[('model', '=', 'import.raw.data')]")

    def import_lead(self):
        if not self.file:
            raise ValidationError(_("Please Upload File to Import !"))
        dup_count = 0
        ins_count = 0
        if self.file_type == 'CSV':
            line = keys = ['name', 'phone', 'email']
            # try:
            csv_data = base64.b64decode(self.file)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            file_reader = []
            csv_reader = csv.reader(data_file, delimiter=',')
            file_reader.extend(csv_reader)
            # except Exception as error:
            # 	print(error)
            # 	raise ValidationError(_("Please Select Valid File Format !"))

            headers = file_reader[0]
            print(headers)
            values = {}
            for i in range(len(file_reader)):
                field = list(map(str, file_reader[i]))
                if values:
                    if i == 0:
                        continue
                    else:
                        values = dict(zip(keys, field))
                        res = self.create_lead(values)
        else:
            try:
                file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                file.write(binascii.a2b_base64(self.file))
                file.seek(0)
                values = {'type': 'lead'}
                imported_values = {}
                workbook = xlrd.open_workbook(file.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:
                raise ValidationError(_("Please Select Valid File Format !"))

            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = list(map(lambda row: row.value.encode('utf-8'), sheet.row(row_no)))
                else:
                    line = list(
                        map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value),
                            sheet.row(row_no)))
                    for f_idx in range(len(fields)):

                        rawValue = line[f_idx]
                        fieldName = fields[f_idx].decode("utf-8")
                        fieldInstance = self.env['crm.lead']._fields[fieldName]
                        columnType = fieldInstance.column_type
                        if columnType[0] == "int4":
                            values[fieldName] = None if line[f_idx] == '' else int(float(line[f_idx]))
                        else:
                            values[fieldName] = rawValue

                    isDuplicated = False
                    if not self.env['crm.lead.storage'].search([('reference_id', '=', self.import_target_storage.id),
                                                                ('phone', '=', values['phone'])]):
                        self.create_lead(values, self.import_target_storage.id)
                        ins_count += 1
                    else:
                        dup_count += 1
                        isDuplicated = True

                    imported_values['import_lead_id'] = self.id
                    imported_values['phone'] = values['phone']
                    imported_values['name'] = values['name']
                    imported_values['source_id'] = values['source_id']
                    imported_values['user_id'] = values['user_id']
                    imported_values['team_id'] = values['team_id']
                    imported_values['reference_id'] = self.import_target_storage.id
                    imported_values['duplicated'] = isDuplicated
                    self.env['import.raw.data'].create(imported_values)

                    if dup_count > 0:
                        self.duplicated_count = dup_count
                    if ins_count > 0:
                        self.inserted_count = ins_count
                    _logger.info(values)
        if self.duplicated_count > 0:
            return {
                'name': _('Check the duplicate data'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('crm_import_lead.import_lead_form_view').id,
                'res_model': 'import.lead',
                'res_id': self.id,
                'type': 'ir.actions.act_window',
            }

        return {
            'name': _('Lead Storage'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm.crm_lead_storage_form').id,
            'res_model': 'crm.lead.storage.ref.info',
            'res_id': self.import_target_storage.id,
            'type': 'ir.actions.act_window',
        }

    def ignore_by_duplicate_data(self):
        return {
            'name': _('Lead Storage'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm.crm_lead_storage_form').id,
            'res_model': 'crm.lead.storage.ref.info',
            'res_id': self.import_target_storage.id,
            'type': 'ir.actions.act_window',
        }

    def renew_by_duplicate_data(self):
        dup_data = self.env['import.raw.data'].search([('import_lead_id', '=', self.id),
                                                       ('duplicated', '=', True)])
        if dup_data:
            values = {'type': 'lead'}
            for f_idx in range(len(dup_data)):
                phone = dup_data[f_idx]['phone']
                reference_id = dup_data[f_idx]['reference_id'].id
                values['phone'] = dup_data[f_idx]['phone']
                values['source_id'] = dup_data[f_idx]['source_id']
                values['user_id'] = dup_data[f_idx]['user_id']
                values['team_id'] = dup_data[f_idx]['team_id']
                values['name'] = dup_data[f_idx]['name']
                condition = [('reference_id', '=', reference_id), ('phone', '=', phone)]
                self.create_lead(values, dup_data[f_idx]['reference_id'].id, condition)

    def create_lead(self, values, reference_id, condition=None):
        lead_storage = self.env['crm.lead.storage']
        if values.get('name') == '':
            raise UserError(_('Name is Required !'))
        if condition:
            old_data = lead_storage.search(condition)
            old_data.unlink()

        values['reference_id'] = int(reference_id)
        lead_storage.create(values)
        return

    def create_lead_storage_reference(self, filename):
        values = {'name': filename, 'owner': self.env.user.id}
        reference_id = self.env['crm.lead.storage.ref.info'].create(values).id
        return reference_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
