# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_back_hover_image = fields.Binary(
        string="Product Back Hover Image")
