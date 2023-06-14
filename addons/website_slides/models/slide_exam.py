
from odoo import fields, models


class SlideExam(models.Model):
    _name = 'slide.exam'
    _description = 'Bộ đề kiểm tra'

    name = fields.Char('Tên đề kiểm tra')
    question_count = fields.Integer('Số lượng câu hỏi')
    question_ids = fields.One2many(
        "slide.question", "exam_id", string="Questions", copy=True)
    select_check = fields.Selection(
        [('Random', 'random'), ('Random Categories ', 'categories'), ('Random All', 'random'), ('Choose question', 'choose')])
