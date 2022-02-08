from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _transfer_form_validate(self, data):
        if self.acquirer_id.provider == 'transfer' and self.acquirer_id.journal_id.is_cod:
            _logger.info('Validated transfer payment for tx %s: set as authorized' % (self.reference))
            self._set_transaction_authorized()
            return True
        else:
            super(PaymentTransaction, self)._transfer_form_validate(data)

    def transfer_s2s_capture_transaction(self):
        if self.acquirer_id.journal_id.is_cod:
            self.acquirer_reference  = self.env.user.name
            self._set_transaction_done()
            self._post_process_after_done()

    def transfer_s2s_void_transaction(self):
        if self.acquirer_id.journal_id.is_cod:
            self._set_transaction_cancel()

class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'
    def _get_feature_support(self):
        res = super(PaymentAcquirer, self)._get_feature_support()
        res['authorize'].append('transfer')
        return res

