# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
{
    'name': "Nav Side Menu Business",
    'description': """Nav Side Menu Business""",
    'category': "Business",
    'author': "73Lines",
    'website': "https://www.73lines.com/",
    'version': "13.0.1.0.1",
    'depends': ['website',
                ],
    'data': [
        'views/assets.xml',
        'views/customize_model_inherit.xml',
        'views/templates.xml',
        'views/website_views.xml',
    ],
    'price': 150,
    'license': 'OPL-1',
    'currency': 'EUR',
    'live_test_url': 'https://www.73lines.com/r/vfd',
    'application': True,
}
