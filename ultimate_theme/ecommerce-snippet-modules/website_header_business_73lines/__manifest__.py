# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Header Layout For Business Theme',
    'summary': 'Layout of website header for business theme',
    'description': 'Layout of website header for business theme',
    'category': 'Website',
    'version': '13.0.1.0.0',
    'author': '73Lines',
    'website': 'https://www.73lines.com/',
    'depends': [
        'website_language_flag_73lines',
    ],
    'data': [
        'views/assets.xml',
        'views/website_header_layout_template.xml',
    ],
    'images': [
        'static/description/website_mid_header.jpg',
    ],
    'installable': True,
    'price': 20,
    'license': 'OEEL-1',
    'currency': 'EUR',
}
