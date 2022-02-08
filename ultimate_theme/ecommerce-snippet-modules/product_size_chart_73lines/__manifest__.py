# -*- coding: utf-8 -*-
{
    'name': 'Product Size Chart By 73Lines',
    'author': '73lines',
    'version': '13.0.1.0.0',
    'summary': 'Product size chart app',
    'website': 'https://www.73lines.com/',
    'sequence': 30,
    'description': """
    application
    """,
    'demo': ['demo/size_chart_demo.xml'],
    'category': 'Managing',
    'depends': ['website', 'website_sale', 'sale'],
    'data': ['security/ir.model.access.csv',
             'views/size_chart_view.xml',
             'views/size_chart_modal.xml',
             'menus/size_chart_menu.xml', ],
    'images': ['static/description/product-size-chart-app-banner.jpg'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
