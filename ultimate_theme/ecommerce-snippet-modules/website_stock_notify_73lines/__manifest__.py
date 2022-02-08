# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Stock Notify',
    'summary': 'Stock Notification module',
    'description': 'Stock Notification module',
    'category': 'Website',
    'version': '13.0.1.0.0',
    'author': '73Lines',
    'website': 'https://www.73lines.com/',
    'depends': ['website_sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/stock_notify_data.xml',
        'views/stock_notify_template.xml',
        'views/stock_notify_view.xml',
    ],
    'images': [
        'static/description/website_stock_notify_73lines.png',
    ],
    'installable': True,
    'price': 40,
    'currency': 'EUR',
    'license': 'OPL-1',
}
