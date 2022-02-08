# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.-
{
    'name': "Nav Side Menu Ecommerce",
    'description': """Nav Side Menu Ecommerce""",
    'category': "Ecommerce",
    'author': "73Lines",
    'website': "https://www.73lines.com/",
    'version': "13.0.1.0.1",
    'depends': ['website_sale_wishlist',
                'website_sale',
                'nav_side_menu_business'],
    'data': [
        'views/templates.xml',
    ],
    'price': 150,
    'license': 'OPL-1',
    'currency': 'EUR',
    'live_test_url': 'https://www.73lines.com/r/vfd',
    'application': True,
}
