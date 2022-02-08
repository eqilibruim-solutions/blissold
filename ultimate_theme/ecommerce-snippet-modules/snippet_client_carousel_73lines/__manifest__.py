# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
{
    'name': 'Website Client Carousel Slider',
    'summary': 'Allows to drag & drop Client Carousel slider in website',
    'description': 'Allows to drag & drop Client Carousel slider in website',
    'category': 'Website',
    'version': '13.0.1.0.0',
    'author': '73Lines',
    'website': 'https://www.73lines.com/',
    'depends': [
        'crm',
        'website_partner',
        'carousel_slider_73lines',
    ],
    'data': [
        'views/assets.xml',
        'views/website_client_template.xml',
        'views/partner_view.xml',
    ],
    'images': [
        'static/description/website_client_carousel_slider_73lines.png',
    ],
    'installable': True,
    'price': 20,
    'license': 'OPL-1',
    'currency': 'EUR',
}
# See LICENSE file for full copyright and licensing details.
