# -*- coding: utf-8 -*-
{
    'name': "solibre_sale_cod",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'website_sale', 'res_city', 'fleet', 'geolocation_share', 'mrp', 'solibre_fleet_gps'],

    # always loaded
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/crm.xml',
        'views/fleet.xml',
        'views/delivery_template.xml',
        'wizard/sale_to_delivery.xml',
        'wizard/sale_tracking.xml',
        'views/sale.xml',
        'views/delivery_schedule.xml',
        'views/sale_order_tracking.xml',
        'views/sale_templates.xml',        
        'views/picking.xml',
        'views/picking.xml',
        'views/journal.xml',
        'views/workorder.xml',
        'views/partner.xml',
        'views/delivery_slip.xml',
        'views/tracking_template.xml',
        'data/mail_delivered.xml',        
    ],
    'qweb': ['static/src/xml/*.xml'],
    # only loaded in demonstration mode

}
