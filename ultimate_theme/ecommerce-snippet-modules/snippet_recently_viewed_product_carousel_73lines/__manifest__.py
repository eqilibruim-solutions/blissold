# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Recently Viewed Product Carousel Snippet',
    'description': 'Recently Viewed Products Carousel Snippet',
    'category': 'Website',
    'version': '13.0.1.0.0',
    'author': '73Lines',
    'website': 'https://www.73lines.com/',
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/recent_product_carousel.xml',
    ],
    'depends': ['snippet_product_carousel_73lines'],
    'images': [
        'static/description/snippet_recently_viewed_products_carousel.jpg',
    ],
    'price': 20,
    'license': 'OPL-1',
    'currency': 'EUR',
}
