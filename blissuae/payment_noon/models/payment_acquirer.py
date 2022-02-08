# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################
from urllib.parse import urlparse,urljoin
import logging
import requests
import json
from odoo.addons.payment_noon.controllers.main import noonController
from odoo.addons.payment.models.payment_acquirer import ValidationError
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
    provider = fields.Selection(selection_add=[('noon', 'Noon')])

    def _get_header(self):
        environment = 'Key_Live' if self.state == 'enabled' else 'Key_Test'
        key = self.sudo().auth_key if environment == 'Key_Live' else self.sudo().test_auth_key
        auth_key = self.sudo().business_id + '.' +self.sudo().app_name+ ':' + key
        auth_key = base64.b64encode(auth_key.encode()).decode()
        return {'Accept': 'text/plain',
                'Content-Type': "application/json",
                'Authorization': '%s %s' % (environment, auth_key)}


    def _get_api_url(self):
        environment = 'Key_Live' if self.state == 'enabled' else 'Key_Test'
        if self.journal_id.company_id.partner_id.country_id.code == 'AE':
            return 'https://api.noonpayments.com/payment/v1'
        elif self.journal_id.company_id.partner_id.country_id.code == 'SA' and environment == 'Key_Test':
            return 'https://api-stg.noonpayments.com/payment/v1'
        else:
            return 'https://api.noonpayments.com/payment/v1'

    def _get_feature_support(self):
        """Get advanced feature support by provider.

        Each provider should add its technical in the corresponding
        key for the following features:
            * fees: support payment fees computations
            * authorize: support authorizing payment (separates
                         authorization and capture)
            * tokenize: support saving payment data in a payment.tokenize
                        object
        """
        res = super(PaymentAcquirernoon, self)._get_feature_support()
        res['authorize'].append('noon')
        return res

    def get_return_url(self):
        site_url =  request.httprequest.environ['HTTP_HOST'].replace('http://', 'https://')
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        base_url = base_url.replace('http://', 'https://')
        url = '%s%s'%(request.httprequest.url_root ,'payment/noon/return')
        return url

    def noon_get_payment_url(self, values):
        headers = self._get_header()
        category = self.category or 'pay'
        profile = self.profile or ''
        url = "%s/order"%self._get_api_url()
        amount = round(values.get('amount'),2)
        txn_reference = values.get('reference')
        data = {"apiOperation": "INITIATE",
                "order": {"reference": txn_reference,
                         "amount": "%s"%amount,
                         "currency": values.get('currency'),
                         "name": txn_reference,
                         "channel": "web",
                         "category": category,},
                "configuration": {"returnUrl": self.get_return_url(),
                                 "locale": "en",
                                 "styleProfile": "bliss_pro"}
                }
        if category in ['auth', 'pay_auth']:
            data["configuration"].update({"paymentAction": "Authorize",})
        else:
            data["configuration"].update({"paymentAction": "Sale",})
        payload = json.dumps(data)
        resp = requests.request('POST', url, data=payload, headers=headers)
        resp = json.loads(resp.text)
        result = resp.get('result')
        _logger.info("NOON INITIATION RESPONSE %s"%resp)
        try:
            order_id = resp.get('result').get('order').get('id')
        except:
            _logger.info("%s %s"%(resp.get('resultCode'),payload))
            raise ValidationError("%s %s"%(resp.get('resultCode'),resp.get('message')))
        try:
            url = result.get('checkoutData').get('postUrl')
        except:
            _logger.info("%s %s"%(resp.get('resultCode'),payload))
            raise ValidationError("%s %s"%(resp.get('resultCode'),resp.get('message')))
        txn = self.env['payment.transaction'].search([('reference', '=', txn_reference)])
        
        if txn and len(txn)==1:
            txn.acquirer_reference = order_id
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
                              'reference': ref,
                              'amount': values.get('amount'),
                              'currency': (values.get('currency')).name  or '',
                              })

        url,reference = self.noon_get_payment_url(noon_tx_values)
        noon_tx_values.update({'payment_url': url,
                               'order_id': reference,
                               'acquirer_reference': reference })

        return noon_tx_values

