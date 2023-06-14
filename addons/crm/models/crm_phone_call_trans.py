from odoo import api, fields, models, tools, SUPERUSER_ID


class PhoneCallTrans(models.Model):
    _name = 'crm.phone.call.trans'
    _description = "Lead/Opportunity reference information"
    _order = "create_date DESC"
    phone = fields.Char('Phone', required=True, readonly=False)
    phone_call_ref_id = fields.Many2one('crm.lead', string='Phone Call')
    call_date = fields.Datetime('Call Date', default=fields.Datetime.now(), readonly=True, copy=False)
    transaction_id = fields.Char('Transaction id', default='', readonly=True)
    record_file = fields.Char('Record file', default='', readonly=True)
    note = fields.Char('Note', default='', readonly=True)
    sipUser = fields.Char('Ext number', default='', readonly=True)
    sipNumber = fields.Char('Call out number', default='', readonly=True)
    totalDuration = fields.Integer('Duration', default=0)
    ringDuration = fields.Integer('Ringing Duration', default=0)
    user_id = fields.Many2one('res.users', string='Sale man')

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)
