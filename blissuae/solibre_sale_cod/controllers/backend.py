# -*- coding: utf-8 -*-

import babel.dates

from datetime import datetime, timedelta, time

from odoo import fields, http, _
from odoo.addons.website_sale.controllers.backend import WebsiteBackend
from odoo.http import request
from odoo.tools.misc import get_lang

import logging
_logger = logging.getLogger(__name__)
    

class WebsiteSaleBackend(WebsiteBackend):

    @http.route()
    def fetch_dashboard_data(self, website_id, date_from, date_to):
        Website = request.env['website']
        current_website = website_id and Website.browse(website_id) or Website.get_current_website()

        results = super(WebsiteSaleBackend, self).fetch_dashboard_data(website_id, date_from, date_to)

        results['dashboards']['sales']['summary'].update(
            order_to_deliver_count=request.env['sale.order'].search_count([
                ('state', 'in', ['sale', 'done']),
                ('order_line', '!=', False),
                ('partner_id', '!=', request.env.ref('base.public_partner').id),
                ('schedule_id', '=', False),
            ]),
        )

        return results