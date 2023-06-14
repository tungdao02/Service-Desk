from odoo import fields, models , api

class HelpdeskPipeline(models.Model):
    _name = "helpdesk.ticket.pipeline"
    _description = "Helpdesk Ticket Pipeline"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    name = fields.Char(required=True, translate=True)
    stages = fields.Many2many(comodel_name="helpdesk.ticket.stage", string="Trạng thái")
    




@api.model
def create(self, vals):
        res = super(HelpdeskPipeline, self).create(vals)
        for stage in res.stages:
            stage.pipeline_id = res.id
        return res

def write(self, vals):
        res = super(HelpdeskPipeline, self).write(vals)
        if "stages" in vals:
            for stage in self.stages:
                stage.pipeline_id = self.id
        return res



