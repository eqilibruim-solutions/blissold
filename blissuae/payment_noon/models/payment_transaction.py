# -*- coding: utf-8 -*-

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

    def _get_header(self):
        acq = self.acquirer_id
        if not acq:
            acq = request.env['payment.acquirer'].search([('provider','=','noon')],limit=1)
        return acq.sudo()._get_header()

    def _get_url(self, acquirer_reference=False):
        acq = self.acquirer_id
        if not acq:
            acq = request.env['payment.acquirer'].search([('provider','=','noon')],limit=1)
        acq = acq.sudo()
        acquirer_reference = acquirer_reference or self.acquirer_reference
        return "%s/order/%s" % (acq._get_api_url(), int(acquirer_reference))


    def action_noon_capture(self):
        return self._update_status()

    def noon_s2s_capture_transaction(self):
        return self.action_noon_capture()


    @api.model
    def _noon_form_get_tx_from_data(self, data):
        """ Given a data dict coming from payumoney, verify it and find the related
        transaction record. """
        acquirer_reference = data.get('orderId')
        if not acquirer_reference:
            raise ValidationError(_('Noon: received data with missing reference (%s)') % (reference))

        result = self.get_status(acquirer_reference)
        msg = ''
        if result:
            order = result.get('order',{}) 
            error_msg = order.get('errorMessage')
            reference = order.get('reference', False)
            nextactions = result.get('nextActions','')
            if reference:
                transaction = self.search([('reference', '=', reference)])


    def get_status(self, acquirer_reference=False):
        url = self._get_url(acquirer_reference)
        headers = self._get_header()
        resp = requests.get(url, headers=headers)
        resp = json.loads(resp.text)
        _logger.info("NOON CHECK STATUS %s"%resp)
        result = resp.get('result',{})
        return result        

    def _update_status(self):
        result = self.get_status()
        if result:
            order = result.get('order',{}) 
            status = order.get('status','') 
            nextactions = result.get('nextActions','')
            if status == 'CAPTURED':
                self._set_transaction_done()
                self._post_process_after_done()
                return True
            elif status == 'AUTHORIZED':
                self._set_transaction_authorized()
                return True
            if 'CAPTURE' in nextactions:
                return self.action_noon_capture()
            else:
                self.write({'state_message': result.get('message', '')})
        return False

    def action_check_status(self):
        if self.acquirer_id.provider == 'noon':
            res = self._update_status()
            return res

    def action_cancel(self):
        if self.acquirer_id.provider == 'noon':
            self.write({'state_message': 'Transaction cancelled by %s'%self.env.user.name})
            res = self._set_transaction_cancel()
            return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
