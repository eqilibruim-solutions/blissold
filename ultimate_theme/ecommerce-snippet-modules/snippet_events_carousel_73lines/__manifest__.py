# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
{
    'name': 'Website Events Carousel Slider',
    'summary': 'Allows to drag & drop Events Carousel slider in website',
    'description': 'Allows to drag & drop Events Carousel slider in website',
    'category': 'Website',
    'version': '13.0.1.0.0',
    'author': '73Lines',
    'website': 'https://www.73lines.com/',
    'depends': [
        'website_event',
        'carousel_slider_73lines',
    ],
    'data': [
        'data/filter_data.xml',
        # 'security/ir.model.access.csv',
        'views/assets.xml',
        'views/website_events_template.xml',
    ],
    'images': [
        'static/description/website_events_carousel_slider_73lines.png',
    ],
    'installable': True,
    'price': 20,
    'license': 'OPL-1',
    'currency': 'EUR',
}
# See LICENSE file for full copyright and licensing details.
