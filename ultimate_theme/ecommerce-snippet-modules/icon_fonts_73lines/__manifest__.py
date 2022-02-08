# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Font Icons by 73lines',
    'summary': 'This modules allows to use different icon fonts '
               'into Odoo Websites.',
    'category': 'Website',
    'description': """
Icon Fonts
==========
This modules allows to use different icon fonts into Odoo Websites.

Currently Available Icon Fonts List:

- Font Awesome

- Stroke

- Fontelico

Working Demo
------------

- https://youtu.be/vokcaEsGj34
""",
    'version': '13.0.1.0.0',
    'author': '73Lines',
    'website': 'https://www.73lines.com/',
    'depends': ['website', 'web_editor'],
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/editor.xml',
    ],
    'images': [
        'static/description/font_icons.jpg'
    ],
    'installable': True,
    'price': 50,
    'license': 'OPL-1',
    'currency': 'EUR',
}
