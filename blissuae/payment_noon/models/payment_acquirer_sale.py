# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################
from urllib.parse import urlparse,urljoin
import logging
import requests
import json
from odoo.addons.payment_noon.controllers.main import noonController
from odoo import api, fields, models, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.tools import float_round
from odoo.tools.float_utils import float_compare
import collections
from odoo.http import request

import base64



_logger = logging.getLogger(__name__)

class PaymentAcquirernoon(models.Model):
    _inherit = 'payment.acquirer'

    business_id = fields.Char('Business ID', required_if_provider='noon')
    auth_key = fields.Char('Auth key', required_if_provider='noon')
    test_auth_key = fields.Char('Test Auth key', required_if_provider='noon')
    app_name = fields.Char('App name', required_if_provider='noon')
    profile = fields.Char('Design Profile')
    category = fields.Char('Category', required_if_provider='noon', default='pay')
    provider = fields.Selection(selection_add=[('noon', 'noon')])

    def get_return_url(self):
        site_url =  request.httprequest.environ['HTTP_HOST'].replace('http://', 'https://')
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url = base_url.replace('http://', 'https://')
        url = '%s%s'%(request.httprequest.url_root ,'payment/noon/return')
        return url

    def noon_get_payment_url(self, values):
        environment = 'Key_Live' if self.state == 'enabled' else 'Key_Test'
        environment = 'Key_Live' if self.state == 'enabled' else 'Key_Test'
        key = self.sudo().auth_key if environment == 'Key_Live' else self.sudo().test_auth_key
        auth_key = self.sudo().business_id + '.' +self.sudo().app_name+ ':' + auth_key
        auth_key = base64.b64encode(auth_key.encode()).decode()
        category = self.category or 'pay'
        profile = self.profile or ''
        headers = {
            'Accept': 'text/plain',
            'Content-Type': "application/json",
            'Authorization': '%s %s' % (environment, auth_key),
            }
        url = "%s/order"%self._get_api_url()
        data = {
                "apiOperation": "INITIATE",
                "order": {
                    "reference": values.get('reference'),
                    "amount": "%s"%values.get('amount'),
                    "currency": values.get('currency'),
                    "name": values.get('reference'),
                    "channel": "web",
                    "category": category,
                },
                "configuration": {
                    "paymentAction": "Sale",
                    "tokenizeCc": "true",
                    "returnUrl": self.get_return_url(),
                    "locale": "en",
                    "styleProfile": "bliss_pro"
                }
            }
        payload = json.dumps(data)

        resp = requests.request('POST', url, data=payload, headers=headers)
        resp = json.loads(resp.text)
        url = resp.get('result').get('checkoutData').get('postUrl')
        order_id = resp.get('result').get('order').get('id')
        return (url,order_id)

    def noon_get_form_action_url(self):
        return request.context.get('tx_url')

    def noon_form_generate_values(self, values):
        self.ensure_one()
        ip = request.httprequest.environ["REMOTE_ADDR"]
        ip_merchant = request.httprequest.environ['SERVER_NAME']

        ref = values.get('reference')
        noon_tx_values = dict()
        noon_tx_values.update({
                              'reference':ref,
                              'amount': int(values.get('amount')),
                              'currency': (values.get('currency')).name  or '',
                              })

        url,reference = self.noon_get_payment_url(noon_tx_values)
        noon_tx_values.update({'payment_url': url,'order_id': reference })

        return noon_tx_values

