# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.http import request


class ProductTemplateRecentView(models.Model):
    _name = 'product.template.recent.view'
    _inherit = ['carousel.slider']
    _order = 'id DESC'

    session_id = fields.Char(string='Session ID', index=True)
    product_id = fields.Many2one('product.template', string='Product')
    user_id = fields.Many2one('res.users', string='User ID')


class Website(models.Model):
    _inherit = 'website'

    def get_recent_products(self):
        uid = request.uid
        recent_products = request.env['product.template.recent.view'].search(
            [('session_id', '=', request.session.sid),
             ('user_id', '=', uid or False)])
        res = {
            'recent_products': recent_products,
        }
        return res
