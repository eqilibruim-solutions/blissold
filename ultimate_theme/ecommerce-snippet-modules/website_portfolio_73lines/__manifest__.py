# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Portfolio',
    'summary': 'Website Portfolio Module',
    'description': 'Website Portfolio Module',
    'category': 'Website',
    'version': '13.0.1.0.0',
    'author': '73Lines',
    'website': 'https://www.73lines.com/',
    'depends': ['website'],
    'data': [
        'security/ir.model.access.csv',
        'data/website_portfolio_data.xml',
        'views/assets.xml',
        'views/website_portfolio_templates.xml',
        'views/website_portfolio_view.xml',
        # 'views/website_portfolio_carousel_snippet.xml',
    ],
    'images': [
        'static/description/website_portfolio_73lines.png',
    ],
    'installable': True,
    'price': 30,
    'license': 'OPL-1',
    'currency': 'EUR',
}
