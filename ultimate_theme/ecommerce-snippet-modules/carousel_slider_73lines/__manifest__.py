# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Carousel Slider',
    'summary': 'Carousel Slider is base module used in other '
               '`snippet_*_carousel_73lines` modules that are '
               'developed by 73lines',
    'description': 'Carousel Slider is base module used in other '
                   '`snippet_*_carousel_73lines` modules that are '
                   'developed by 73lines',
    'category': 'Website',
    'version': '13.0.1.0.1',
    'author': '73Lines',
    'website': 'https://www.73lines.com/',
    'data': [
        'views/assets.xml',
        'views/carousel_snippet_options.xml',
    ],
    'depends': ['website', 'rating'],
    'images': [
        'static/description/carousel_slider_73lines.png'
    ],
    'installable': True,
    'price': 50,
    'license': 'OPL-1',
    'currency': 'EUR',
}
