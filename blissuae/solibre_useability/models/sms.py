from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)

class SmsComposer(models.TransientModel):
    _inherit = 'sms.composer'

    def action_send_whatsapp(self):
        if self.composition_mode in ('numbers', 'comment') and self.recipient_invalid_count:
            raise UserError(_('%s invalid recipients') % self.recipient_invalid_count)
        self._action_send_whatsapp()
        return False

    def _action_send_whatsapp(self):
        records = self._get_records()
        _logger.info(self.composition_mode)
        if self.composition_mode == 'numbers':
            return self._action_send_whatsapp_numbers()
        elif self.composition_mode == 'comment':
            if records is not None and issubclass(type(records), self.pool['mail.thread']):
                return self._action_send_whatsapp_comment(records)
            return self._action_send_whatsapp_numbers()
        else:
            return self._action_send_whatsapp_mass(records)

    def _action_send_whatsapp_numbers(self):
        self.env['whatsapp.api']._send_whatsapp_batch([{
            'res_id': 0,
            'number': number,
            'content': self.body,
        } for number in self.sanitized_numbers.split(',')])
        return True

    def _action_send_whatsapp_comment(self, records=None):
        records = records if records is not None else self._get_records()
        subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')

        messages = self.env['mail.message']
        for record in records:
            messages |= record._message_whatsapp(
                self.body, subtype_id=subtype_id,
                partner_ids=self.partner_ids.ids or False,
                number_field=self.number_field_name,
                whatsapp_numbers=self.sanitized_numbers.split(',') if self.sanitized_numbers else None)
        return messages

    def _action_send_whatsapp_mass(self, records=None):
        records = records if records is not None else self._get_records()

        sms_record_values = self._prepare_mass_sms_values(records)
        sms_all = self._prepare_mass_sms(records, sms_record_values)

        if sms_all and self.mass_keep_log and records and issubclass(type(records), self.pool['mail.thread']):
            log_values = self._prepare_mass_log_values(records, sms_record_values)
            records._message_log_batch(**log_values)

        if sms_all and self.mass_force_send:
            sms_all.filtered(lambda sms: sms.state == 'outgoing').send(auto_commit=False, raise_exception=False)
            return self.env['sms.sms'].sudo().search([('id', 'in', sms_all.ids)])
        return sms_all


class SmsSms(models.Model):
    _inherit = 'sms.sms'

    def send_whatsapp(self, delete_all=False, auto_commit=False, raise_exception=False):
        """ Main API method to send SMS.

          :param delete_all: delete all SMS (sent or not); otherwise delete only
            sent SMS;
          :param auto_commit: commit after each batch of SMS;
          :param raise_exception: raise if there is an issue contacting IAP;
        """
        for batch_ids in self._split_batch():
            self.browse(batch_ids)._send_whatsapp(delete_all=delete_all, raise_exception=raise_exception)
            # auto-commit if asked except in testing mode
            if auto_commit is True and not getattr(threading.currentThread(), 'testing', False):
                self._cr.commit()


    def _send_whatsapp(self, delete_all=False, raise_exception=False):
        """ This method tries to send SMS after checking the number (presence and
        formatting). """
        iap_data = [{
            'res_id': record.id,
            'number': record.number,
            'content': record.body,
        } for record in self]

        try:
            iap_results = self.env['whatsapp.api']._send_whatsapp_batch(iap_data)
        except Exception as e:
            _logger.info('Sent batch %s SMS: %s: failed with exception %s', len(self.ids), self.ids, e)
            if raise_exception:
                raise
            self._postprocess_iap_sent_sms([{'res_id': sms.id, 'state': 'server_error'} for sms in self], delete_all=delete_all)
        else:
            _logger.info('Send batch %s SMS: %s: gave %s', len(self.ids), self.ids, iap_results)
            self._postprocess_iap_sent_sms(iap_results, delete_all=delete_all)

