# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Products Category Snippet',
    'summary': 'Allows to drag & drop product category snippet '
               'in website',
    'description': 'Allows to drag & drop product category snippet '
                   ' in website',
    'category': 'Website',
    'version': '12.0.1.0.0',
    'author': '73Lines',
    'website': 'https://www.73lines.com/',
    'data': [
        'data/filter_data.xml',
        'views/assets.xml',
        'views/product_category_snippet.xml',
    ],
    'depends': ['website_sale', 'carousel_slider_73lines'],
    'images': [
        'static/description/snippet_product_category_snippet.jpg',
    ],
    'installable': True,
    'price': 20,
    'license': 'OPL-1',
    'currency': 'EUR',
}
