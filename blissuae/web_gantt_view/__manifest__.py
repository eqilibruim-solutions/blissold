# -*- coding: utf-8 -*-
#╔══════════════════════════════════════════════════════════════════╗
#║                                                                  ║
#║                ╔═══╦╗       ╔╗  ╔╗     ╔═══╦═══╗                 ║
#║                ║╔═╗║║       ║║ ╔╝╚╗    ║╔═╗║╔═╗║                 ║
#║                ║║ ║║║╔╗╔╦╦══╣╚═╬╗╔╬╗ ╔╗║║ ╚╣╚══╗                 ║
#║                ║╚═╝║║║╚╝╠╣╔╗║╔╗║║║║║ ║║║║ ╔╬══╗║                 ║
#║                ║╔═╗║╚╣║║║║╚╝║║║║║╚╣╚═╝║║╚═╝║╚═╝║                 ║
#║                ╚╝ ╚╩═╩╩╩╩╩═╗╠╝╚╝╚═╩═╗╔╝╚═══╩═══╝                 ║
#║                          ╔═╝║     ╔═╝║                           ║
#║                          ╚══╝     ╚══╝                           ║
#║ SOFTWARE DEVELOPED AND SUPPORTED BY ALMIGHTY CONSULTING SERVICES ║
#║                   COPYRIGHT (C) 2016 - TODAY                     ║
#║                   http://www.almightycs.com                      ║
#║                                                                  ║
#╚══════════════════════════════════════════════════════════════════╝
# Module Was Migrated from Odoo v8: partial code reference taken 
# from v8 gantt view module but structure is rewritten.
{
    "name": "Web Gantt View",
    "version": "1.0.2",
    "author": "Almighty Consulting Services",
    "category": "Tools",
    'description': """Odoo Web Gantt chart view. gantt view gantt chart project gantt chart""",
    "summary": """Odoo Web Gantt chart view.""",
    'depends': ['web'],
    'data' : [
        'views/web_gantt.xml', 
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'images': [
         'static/description/gantt_view_turkeshpatel_almihgtycs.png',
     ],
    'auto_install': True,
    'installable': True,
    "price": 12,
    "currency": "EUR",
}
