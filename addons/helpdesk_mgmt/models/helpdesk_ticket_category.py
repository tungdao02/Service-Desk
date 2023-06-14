from odoo import fields, models , api


class HelpdeskCategory(models.Model):

    _name = "helpdesk.ticket.category"
    _description = "Helpdesk Ticket Category"
    _order = "sequence, id"


    sequence = fields.Integer(default=10)
    active = fields.Boolean(
        default=True,
    )
    name = fields.Char(
        required=True,
        translate=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    
    
    mother_category_id = fields.Many2one(comodel_name="helpdesk.ticket.mother.category",  string="Danh mục")



    @api.onchange("mother_category_id")
    def printmci(self):
        print(self.mother_category_id)



class HelpdeskMotherCategory(models.Model):

    _name = "helpdesk.ticket.mother.category"
    _description = "Helpdesk Ticket Mother Category"
    _order = "sequence, id"


    sequence = fields.Integer(default=10)
    active = fields.Boolean(
        default=True,
    )
    name = fields.Char(
        required=True,
        translate=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    
    category_ids = fields.Many2many(
        comodel_name="helpdesk.ticket.category",    
        
        string="Danh mục phụ",
    )



    # @api.onchange("category_ids")
    # def _onchange_category_ids(self):
    #     for category in self.category_ids:
    #         category.mother_category_id = self.env.context.get("default_mother_category_id")
    #         print(category.mother_category_id, self.id)
            
        
            
                

  
    @api.model
    def create(self, vals):
        res = super(HelpdeskMotherCategory, self).create(vals)
        for category in res.category_ids:
            # if(category.mother_category_id is None):
                category.mother_category_id = res.id
                
        print(res)
        return res
    
    def write(self, vals):
        res = super(HelpdeskMotherCategory, self).write(vals)
        if 'category_ids' in vals:
            for category in self.category_ids:
            #  if(category.mother_category_id is None):
                print(category.mother_category_id, self.id)
                category.mother_category_id = self.id
                print(type(category.mother_category_id), self.id)
        
        return res
