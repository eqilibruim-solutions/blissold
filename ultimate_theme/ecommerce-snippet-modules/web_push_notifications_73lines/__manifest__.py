# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Web Push Notifications',
    'version': '13.0.1.0.0',
    'category': 'Website',
    'summary': 'Web Push Notifications',
    'website': 'https://www.73lines.com/',
    'author': '73Lines',
    'description': """
Support web push notifications provided by *OneSignal*.
=======================================================

This module allows to sends personalized push notifications
to subscribed users from websites.

Supported Web Browsers List
---------------------------
* Google Chrome
* Mozilla Firefox
* Apple Safari

Module only works for secure websites (with *HTTPS://*).

Please, read the *"doc/index.rst"* file for *"How to Configure?"*.

""",
    'depends': ['website'],
    'data': [
        'views/website_templates.xml',
    ],
    'images': [
        'static/description/web_push_notifications.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 30,
    'license': 'OPL-1',
    'currency': 'EUR',
}
