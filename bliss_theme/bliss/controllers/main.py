from odoo import http, tools, api, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):

    @http.route('/shop/products/best_sellers', type='json', auth='public', website=True)
    def products_best_sellers(self, **kwargs):
        return self._get_products_best_sellers()

    def _get_products_best_sellers(self):

        bestsellers_products = request.env['product.product'].with_context(display_default_code=False).search([],
                                                                                                              limit=12)
        FieldMonetary = request.env['ir.qweb.field.monetary']
        monetary_options = {
            'display_currency': request.website.get_current_pricelist().currency_id,
        }
        rating = request.website.viewref('website_sale.product_comment').active
        res = {'products': []}
        for product in bestsellers_products:
            combination_info = product._get_combination_info_variant()
            res_product = product.read(['id', 'name', 'website_url'])[0]
            res_product.update(combination_info)
            res_product['price'] = FieldMonetary.value_to_html(res_product['price'], monetary_options)
            if rating:
                res_product['rating'] = request.env["ir.ui.view"].render_template(
                    'website_rating.rating_widget_stars_static', values={
                        'rating_avg': product.rating_avg,
                        'rating_count': product.rating_count,
                    })
            res['products'].append(res_product)

        return res
