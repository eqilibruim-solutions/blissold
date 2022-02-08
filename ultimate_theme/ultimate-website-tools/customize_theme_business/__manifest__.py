# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Customize Theme Business',
    'category': "Business",
    'author': "73Lines",
    'website': "https://www.73lines.com/",
    'version': "13.0.1.0.1",
    'depends': [

        # Default Modules
        'theme_default',
        # 'google_dynamic_font',


    ],
    'data': [
        'views/assests.xml',
        'views/customize_model.xml',
        'views/navbar_headers.xml',
        'views/s_custom_button.xml',
    ],
    'price': 150,
    'license': 'OPL-1',
    'currency': 'EUR',
    'live_test_url': 'https://www.73lines.com/r/vfd',
    'application': True,
}

