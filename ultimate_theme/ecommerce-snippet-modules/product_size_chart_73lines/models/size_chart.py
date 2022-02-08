# * - coding: utf - 8 -
from odoo import api, fields, models


class SizeChart(models.Model):
    _name = "size.chart"
    _description = "Size Chart"

    name = fields.Char(string="Title")
    image = fields.Binary()
    categories = fields.Many2many('product.public.category', string="Categories")
    chart = fields.Char(string="Size Chart")
    size_details = fields.Char(string="Size Detail")
