# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleStockNotify(WebsiteSale):
    @http.route(['/shop/notify'], type='http', auth="public", website=True)
    def notify_by_email(self, **post):
        notify_info = {
            'name': 'Notify for ' + request.env[
                'product.product'].sudo().browse(
                int(post['out_stock_product_id'])).name,
            'product': post['out_stock_product_id'],
            'email': post['notify_email'],
            'created_on': datetime.today(),
            'state': 'draft',
        }
        request.env['stock.notify'].sudo().create(notify_info)

    def get_attribute_value_ids(self, product):
        """ list of selectable attributes of a product

        :return: list of product variant description
           (variant id, [visible attribute ids], variant price,
           variant sale price)
        """
        # product attributes with at least two choices
        product = product.with_context(quantity=1)

        visible_attrs_ids = product.attribute_line_ids.filtered(
            lambda l: len(l.value_ids) > 1).mapped('attribute_id').ids
        to_currency = request.website.get_current_pricelist().currency_id
        attribute_value_ids = []
        for variant in product.product_variant_ids:
            if to_currency != product.currency_id:
                price = variant.currency_id._convert(
                    variant.website_public_price, to_currency, request.env.user.company_id, datetime.today())
            else:
                price = variant.website_public_price
            visible_attribute_ids = [v.id for v in variant.attribute_value_ids
                                     if v.attribute_id.id in visible_attrs_ids]
            attribute_value_ids.append(
                [variant.id, visible_attribute_ids, variant.website_price,
                 price, variant.qty_available])
        return attribute_value_ids
