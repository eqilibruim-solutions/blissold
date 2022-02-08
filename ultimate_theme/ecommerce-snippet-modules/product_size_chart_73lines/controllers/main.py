# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, tools, _
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class Website(WebsiteSale):

    @http.route()
    def product(self, product, category='', search='', **kwargs):
        product_context = dict(request.env.context,
                               active_id=product.id,
                               partner=request.env.user.partner_id)
        ProductCategory = request.env['product.public.category']

        if category:
            category = ProductCategory.browse(int(category)).exists()
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}
        keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)
        categs = ProductCategory.search([('parent_id', '=', False)])
        pricelist = request.website.get_current_pricelist()

        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency.compute(price, to_currency)

        if not product_context.get('pricelist'):
            product_context['pricelist'] = pricelist.id
            product = product.with_context(product_context)

        size_chart = request.env['size.chart'].search([('categories', 'in', product.public_categ_ids.ids)])
        values = {
            'search': search,
            'category': category,
            'pricelist': pricelist,
            'attrib_values': attrib_values,
            'compute_currency': compute_currency,
            'attrib_set': attrib_set,
            'keep': keep,
            'categories': categs,
            'main_object': product,
            'product': product,
            'get_attribute_exclusions': self._get_attribute_exclusions,
            'size_chart': size_chart,
        }
        return request.render("website_sale.product", values)
