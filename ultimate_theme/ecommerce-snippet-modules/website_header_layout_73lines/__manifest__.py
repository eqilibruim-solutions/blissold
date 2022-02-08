# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Header Layout',
    'summary': 'Layout of website header',
    'description': 'Layout of website header',
    'category': 'Website',
    'version': '13.0.1.0.0',
    'author': '73Lines',
    'website': 'https://www.73lines.com/',
    'depends': [
        'website_language_flag_73lines',
        'website_sale_wishlist',
        'website_header_business_73lines',
    ],
    'data': [
        'views/assets.xml',
        'views/website_header_layout_template.xml',
    ],
    'images': [
        'static/description/website_header_layout_73lines.png',
    ],
    'installable': True,
    'price': 20,
    'license': 'OPL-1',
    'currency': 'EUR',
}
