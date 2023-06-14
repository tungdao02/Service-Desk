from importlib_resources._common import _
from odoo import fields, models
import odoo
from odoo import SUPERUSER_ID
from odoo.exceptions import AccessDenied, AccessError
from odoo.exceptions import UserError
import requests
import response

import odoo.release
import odoo.sql_db
import odoo.tools
from odoo.sql_db import db_connect
from odoo.release import version_info
from odoo.tools import find_pg_tool, exec_pg_environ

SUCCESS_CODE = 9999


def prepare_header_access_token(self):
    base_api = odoo.tools.config.options['omi_call_base_api']

    access_token = self.env['crm.res.config.settings'].search([('key', '=', 'access_token')]).value

    if not access_token:
        url = base_api.format(endpoint='auth?apiKey={api_key}'.format(api_key=odoo.tools.config.options['omi_call_apikey']))
        res = requests.get(url)
        payload = res.json()['payload']
        if len(payload) != 0:
            access_token = res.json()['payload']['access_token']
            key = self.env['crm.res.config.settings'].search([('key', '=', 'access_token')])
            if len(key.ids) != 0:
                key.update({'value': access_token})
            else:
                self.env['crm.res.config.settings'].create({'key': 'access_token', 'value': access_token})
        else:
            return False
    return {'Authorization': 'Bearer ' + access_token}


def try_request(self, url, is_post_request=True, data=None):
    headers = prepare_header_access_token(self)
    if not headers:
        raise AccessError(_('Unable to authorize Call Service.'))
    res = requests.get(url, headers=headers) if not is_post_request else requests.post(url, headers=headers, data=data)
    if res.content == 'Unauthorized':
        headers = prepare_header_access_token(self)
        if not headers:
            return False
        else:
            res = requests.get(url, headers=headers, data=data)
    return res


def get_trans_record_file(self, trans_id):
    try:
        url = odoo.tools.config.options['omi_call_base_api'] \
            .format(endpoint=odoo.tools.config.options['omi_call_trans_detail'].format(transaction_id=trans_id))
        res = try_request(self, url, True).json()
        if res['status_code'] == SUCCESS_CODE:
            return res['payload']['recording_file']
        return None
    except Exception as e:
         raise UserError(e)


class CrmPhoneExtNumberSync(models.TransientModel):
    _name = 'crm.phone.ext.number.sync'
    _description = 'crm.phone.ext.number.sync'
    user_id = fields.Many2one(comodel_name='res.users', string='Identifier')
    role_name = fields.Selection([('Sale', 'Sale'), ('Lead', 'Lead'), ('Admin', 'Admin')], string= 'Roles')

    def action_sync(self):
        print(odoo.tools.config.options)
        try:
            url = odoo.tools.config.options['omi_call_base_api'] \
                .format(endpoint=odoo.tools.config.options['omi_call_get_phone'])

            res = try_request(self, url, False)
            items = res.json()['payload']['items']
            if len(items) > 0:
                sip_users = []
                for item in items:
                    sip_user = item['sip_user']
                    ext_number = self.env['crm.phone.ext.number'].search([('ext_number', '=', sip_user)])
                    if len(ext_number) == 0:
                        values = {'ext_number': sip_user, 'password': item['password'], 'domain': item['domain'],
                                  'public_number': item['public_number'], 'full_name': item['full_name'],
                                  'email': item['email'], 'enabled': item['enabled']}
                        self.env['crm.phone.ext.number'].create(values)
                    sip_users.append(sip_user)
                self.env['crm.phone.ext.number'].search([('ext_number', 'not in', sip_users)]) \
                    .update({'is_active': False})
            return {
                'name': 'Ext Numbers List',
                'view_type': 'tree',
                'view_mode': 'tree',
                'view_id': self.env.ref('crm.crm_phone_ext_number_tree').id,
                'res_model': 'crm.phone.ext.number',
                'type': 'ir.actions.act_window',
            }
        except:
            raise AccessError('Unable to retrieve data from Call Service.')

    def action_add(self):
        print(odoo.tools.config.options)
        url = odoo.tools.config.options['omi_call_base_api'] \
            .format(endpoint=odoo.tools.config.options['omi_call_invite_agent'])
        owner_email = odoo.tools.config.options['omi_call_owner_email']

        try:
            payload = "{"+"'owner_email':'{owner_email}', 'role_name':'{role_name}','password':'{password}'," \
                      "'identify_info':'{identify_info}','full_name':'{full_name}'" \
                .format(owner_email=owner_email, role_name=self.role_name,
                        password=odoo.tools.config.options['omi_call_init_password'],
                        identify_info=self.user_id.email,
                        full_name=self.user_id.name)+"}"
            res = try_request(self, url, True, payload).json()
            if res['status_code'] == SUCCESS_CODE:
                self.action_sync(self)
            else:
                raise AccessError(res['message'])
        except:
            raise AccessError('Unable to retrieve data from Call Service.')
