# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, exceptions
from odoo.addons.iap.models import iap
import requests
import logging

_logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = 'https://api.twilio.com/2010-04-01'

class IapAccount(models.Model):
    _inherit = 'iap.account'    

    sender = fields.Char(string="Sender")


class WhatsappApi(models.AbstractModel):
    _name = 'whatsapp.api'
    _description = 'WhatsApp API'

    @api.model
    def _contact_iap(self, local_endpoint, params):
        return

    @api.model
    def _send_whatsapp(self, numbers, message):
        """ Send a single message to several numbers

        :param numbers: list of E164 formatted phone numbers
        :param message: content to send

        :raises ? TDE FIXME
        """
        params = {
            'To': 'whatsapp:%s'%numbers,
            'Body': message,
        }
        return self._contact_iap('/Accounts', params)

    @api.model
    def _send_whatsapp_batch(self, messages):
        """ Send SMS using IAP in batch mode

        :param messages: list of SMS to send, structured as dict [{
            'res_id':  integer: ID of sms.sms,
            'number':  string: E164 formatted phone number,
            'content': string: content to send
        }]

        :return: return of /iap/sms/1/send controller which is a list of dict [{
            'res_id': integer: ID of sms.sms,
            'state':  string: 'insufficient_credit' or 'wrong_number_format' or 'success',
            'credit': integer: number of credits spent to send this SMS,
        }]

        :raises: normally none
        """
        return