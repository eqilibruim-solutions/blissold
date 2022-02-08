# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Theme Customize Ecommerce',
    'description': 'Theme Customize Ecommerce',
    'category': "Ecommerce",
    'author': "73Lines",
    'website': "https://www.73lines.com/",
    'version': "13.0.1.0.1",
    'depends': [

        # Dependency Modules
        'customize_theme_business',
        'website_sale',
        'website_sale_wishlist',

    ],
    'data': [
        'views/assests.xml',
        'views/customize_model.xml',
        'views/navbar_headers.xml',
        'views/category_view_inherit.xml',
        'views/category_breadcrumbs.xml',
    ],
    'price': 150,
    'license': 'OPL-1',
    'currency': 'EUR',
    'live_test_url': 'https://www.73lines.com/r/vfd',
    'application': True,
}

