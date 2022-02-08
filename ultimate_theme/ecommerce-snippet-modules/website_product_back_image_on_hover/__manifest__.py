# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Product Back Image On Hover',
    'summary': 'Website Product Back Image On Hover',
    'description': 'Website Product Back Image On Hover',
    'category': 'Website',
    'version': '13.0.1.0.0',
    'author': '73Lines',
    'website': 'https://www.73lines.com/',
    'depends': ['website', 'website_sale'],
    'data': [
        'views/assets.xml',
        'views/product_view.xml',
        'views/template.xml'
    ],
    'images': [
        'static/description/website_product_back_image_on_hover_73lines.png'
    ],
    'installable': True,
    'price': 49,
    'license': 'OPL-1',
    'currency': 'EUR',
    'Application': True,
}
