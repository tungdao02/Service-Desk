# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Users(models.Model):
    _inherit = 'res.users'

    phone_ext_numbers = fields.Many2many('crm.phone.ext.number', 'user_ext_rel', 'user_id',
                                         'ext_id', string='Ext Phone Number')
    target_sales_won = fields.Integer('Won in Opportunities Target')
    target_sales_done = fields.Integer('Activities Done Target')
    leads_assigned_ids = fields.One2many('crm.lead', 'user_id')

    def view_lead_assigned(self):
        print('view_lead_assigned')
        return {
            'name': 'Lead assigned',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('crm.crm_user_my_customer').id,
            'res_model': 'res.users',
            'res_id': self.env.user.id,
            'type': 'ir.actions.act_window',
        }
