from odoo import models, fields


class NumberManage(models.Model):
    _name = 'crm.numbermanage'
    _description = 'telecom number manage'

    name = fields.Datetime(string="Lịch sử cuộc gọi", required=True,
                           default=lambda self: fields.Datetime.now())
    phone_number_head = fields.Selection([(
        '032', '032'), ('033', '033'), ('034', '034'), ('035', '035'), ('036', '036'), ('037', '037'), ('038', '038'), ('039', '039'), ('058', '058'), ('056', '056'),  ('070', '070'), ('076', '076'), ('077', '077'), ('078', '078'), ('079', '079'), ('081', '081'), ('082', '082'), ('083', '083'), ('084', '084'), ('085', '085'), ('086', '086'), ('088', '088'), ('089', '089'), ('090', '090'), ('091', '091'), ('092', '092'), ('093', '093'), ('094', '094'), ('096', '096'), ('097', '097'), ('098', '098')], string="Đầu số", required=True, default='032')
    telecom_operator = fields.Selection([('viettel', 'Viettel'), ('vinaphone', 'Vinaphone'), (
        'mobiphone', 'Mobiphone'), ('vietnamobile', 'Vietnamobile')], string='Nhà mạng', default='viettel', required=True)
