# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################

import logging
import requests
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.float_utils import float_compare
from odoo.tools.translate import _
from odoo import api, fields, models
from odoo.http import request
_logger = logging.getLogger(__name__)
import base64
import json

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    _noon_valid_tx_status = 'success'
    _noon_decline_tx_status = 'fail'

# --------------------------------------------------
# FORM RELATED METHODS
# --------------------------------------------------

    @api.model
    def _noon_form_get_tx_from_data(self, data):
        """ Given a data dict coming from payumoney, verify it and find the related
        transaction record. """
        reference = data.get('merchantReference')
        if not reference:
            raise ValidationError(_('Noon: received data with missing reference (%s)') % (reference))

        transaction = self.search([('reference', '=', reference)])

        if not transaction:
            error_msg = (_('Noon: received data for reference %s; no order found') % (reference))
            raise ValidationError(error_msg)
        elif len(transaction) > 1:
            error_msg = (_('Noon: received data for reference %s; multiple orders found') % (reference))
            raise ValidationError(error_msg)

        return transaction

    def _get_payment_status(self):
        acq = self.acquirer_id
        environment = 'Key_Live' if acq.state == 'enabled' else 'Key_Test'
        auth_key = acq.sudo().auth_key
        if environment == 'Key_Test':
            auth_key = acq.sudo().test_auth_key            

        auth_key = acq.sudo().business_id + '.' +acq.sudo().app_name+ ':' + auth_key
        auth_key = base64.b64encode(auth_key.encode()).decode()
        headers = {
            'Accept': 'text/plain',
            'Content-Type': "application/json",
            'Authorization': '%s %s' % (environment, auth_key),
            }
        url = "%s/order/%s"%(self.acquirer_id._get_api_url(),int(self.acquirer_reference))
        resp = requests.get(url, headers=headers)
        resp = json.loads(resp.text)
        result = resp.get('result',{})
        if result:
            order = result.get('order',{}) 
            status = order.get('status','')   
            msg = order.get('errorMessage','')  
            events = result.get('events',[])
        return order, status, msg, events
        #check next action if contains captured
        #call Capture api

    def _check_payment_status(self):
        order, status, msg, events = self._get_payment_status()
        _logger.info("NOON RESP Order%s"%order)
        _logger.info("NOON RESP Status%s"%status)
        _logger.info("NOON RESP MSG%s"%msg)
        _logger.info("NOON RESP EVENTS%s"%events)

        if not order:
            self._set_transaction_error('Payment not processed')
            return False
        elif status == 'CAPTURED':
            self._set_transaction_done()
            return True
        elif msg:
            self.write({'state_message': msg})
            self._set_transaction_cancel()
            return False
        else:
            self._set_transaction_done()
        self._set_transaction_pending()
        return True


    def _noon_action_force_done(self):
        _logger.info(self.acquirer_id.provider)
        if self.acquirer_id.provider == 'noon':
            res = self._check_payment_status()
            #self._post_process_after_done()
            return res


    def _noon_form_validate(self, data):
        status = data.get('result')
        result = self.write({
            'acquirer_reference': data.get('orderId'),
            'date': fields.Datetime.now(),
        })
        return self._check_payment_status()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
