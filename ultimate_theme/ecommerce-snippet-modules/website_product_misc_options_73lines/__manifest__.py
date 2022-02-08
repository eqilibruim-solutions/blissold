# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Product Miscellaneous Options',
    'summary': 'MISC Options like... Tags, Brands, View Limit, '
               'View Switcher, Price Filter',
    'description': 'MISC Options like... Tags, Brands, View Limit, '
                   'View Switcher, Price Filter',
    'category': 'Website',
    'version': '13.0.1.0.0',
    'author': '73Lines',
    'website': 'https://www.73lines.com/',
    'depends': ['website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_limit_data.xml',
        'views/assets.xml',
        'views/templates.xml',
        'views/brand_template.xml',
        'views/product_limit_view.xml',
        'views/product_views.xml',
    ],
    'demo': [
        'data/brand_menu_data.xml'
    ],
    'images': [
        'static/description/website_product_misc_options_73lines.png',
    ],
    'installable': True,
    'price': 99,
    'license': 'OPL-1',
    'currency': 'EUR',
}
