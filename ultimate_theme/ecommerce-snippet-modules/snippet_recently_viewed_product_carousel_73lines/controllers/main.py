# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class RecentProducts(WebsiteSale):

    @http.route()
    def product(self, product, category='', search='', **kwargs):
        uid = request.uid
        record = request.env['product.template.recent.view'].search(
            [('session_id', '=', request.session.sid),
             ('product_id', '=', product.id),
             ('user_id', '=', uid or False)])
        if not record:
            request.env['product.template.recent.view'].create({
                'session_id': request.session.sid,
                'product_id': product.id,
                'user_id': uid or False,
            })

        return super(RecentProducts, self).product(product, category,
                                                   search, **kwargs)
