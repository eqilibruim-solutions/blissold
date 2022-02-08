# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################
import json
import logging
import pprint
from urllib.parse import urlparse,urljoin
import requests
import werkzeug
from odoo import http, tools, _
from odoo.http import request
from odoo import SUPERUSER_ID
import pprint
import werkzeug
_logger = logging.getLogger(__name__)

from odoo.osv import expression
from odoo.addons.website_sale.controllers.main import WebsiteSale


class noonController(http.Controller):
    _cancel_url = '/payment/noon/cancel'
    _exception_url = '/payment/noon/error'
    _return_url = '/payment/noon/return'
    

    @http.route([_return_url, _cancel_url, _exception_url], type='http', auth='public' , csrf=False)
    def noon_return(self, **post):
        _logger.info(
            'Noon: entering form_feedback with post data %s', pprint.pformat(post))
        if post:
            request.env['payment.transaction'].sudo().form_feedback(post, 'noon')
        return werkzeug.utils.redirect('/payment/process')

