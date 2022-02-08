# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "City List",
    'description': "Select city from list",
    'category': 'Contact',
    'version': '1.0',
    'depends': ['base', 'point_of_sale', 'website_sale'],
    'data': [
        'views/partner.xml',
        'views/city.xml',
        # 'views/sale.xml',
        'views/zone.xml',
        'views/country.xml',
        'views/carrier.xml',
        'views/templates.xml',
        'data/delivery_smsa_data.xml',
        'security/ir.model.access.csv'
    ],
    "qweb": [
        "static/src/xml/pos.xml",
    ],
    'license': 'OEEL-1',
    'uninstall_hook': 'uninstall_hook',
}
