# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Google Dynamic Font',
    'category': 'Tools',
    'version': '13.0.1.0.0',
    'description':
        """
Google Dynamic Font
===================

This module provides the Add and Remove Google Fonts.
        """,
    'depends': ['website'],
    'data': [
        'views/templates.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'installable': True,
    'price': 50,
    'license': 'OPL-1',
    'currency': 'EUR',
}
