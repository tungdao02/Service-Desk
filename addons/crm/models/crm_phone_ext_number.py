from odoo import api, fields, models, tools, SUPERUSER_ID, _


class PhoneExtNumber(models.Model):
    _name = 'crm.phone.ext.number'
    _description = 'Ext Number'
    ext_number = fields.Char(string="Ext Number", require=True)
    password = fields.Char()
    domain = fields.Char()
    public_number = fields.Char()
    full_name = fields.Char()
    email = fields.Char()
    enabled = fields.Boolean()
    user_ids = fields.Many2many('res.users', 'user_ext_rel', 'ext_id',
                                'user_id', string='Sale Man', default=None)
    is_active = fields.Boolean(default=True)
