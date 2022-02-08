from odoo import models, fields, api, exceptions, _
import requests

import logging

_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'
    _order = 'sequence'

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def action_force_done(self):
        if hasattr(self, '_%s_action_force_done' % self.acquirer_id.provider):
            return getattr(self, '_%s_action_force_done' % self.acquirer_id.provider)()

        if self.acquirer_id.provider != 'transfer':
            raise exceptions.ValidationError("You can only validate manual payment types") 
        self._set_transaction_done()
        self._post_process_after_done()
        return True

    def _transfer_form_validate(self, data):
        if self.acquirer_id.name == 'PayLink':
            return True
        else:
            return super(PaymentTransaction, self)._transfer_form_validate(data)



