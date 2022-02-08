# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo import api, fields


class ProductPublicCategory(models.Model):
    _name = 'product.public.category'
    _inherit = ['product.public.category', 'carousel.slider']


class Website(models.Model):
    _inherit = 'website'

    # @api.multi
    def get_categories(self):
        category_ids = self.env['product.public.category'].search(
            [('parent_id', '=', False)])
        res = {
            'categories': category_ids,
        }
        return res
