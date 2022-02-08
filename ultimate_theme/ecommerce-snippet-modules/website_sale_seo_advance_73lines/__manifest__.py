# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Sale SEO Advance by 73Lines',
    'description': 'Website Sale SEO Advance by 73Lines',
    'category': 'Website',
    'version': '13.0.1.0.0',
    'author': '73Lines',
    'depends': ['website_sale', 'mail'],
    'website': 'https://www.73lines.com',
    'summary': 'Website Sale SEO Advance',
    'data': [
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/product_seo_config.xml',
    ],
    'images': [
        'static/description/website_sale_seo_advance_73lines.jpg',
    ],
    'installable': True,
    'price': 40,
    'currency': 'EUR',
    'license': 'OPL-1',
}
