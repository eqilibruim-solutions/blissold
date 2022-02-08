from odoo import models, fields, api, exceptions, _
from odoo.tools import html2plaintext
from odoo.addons.phone_validation.tools import phone_validation

import logging

_logger = logging.getLogger(__name__)

class Notification(models.Model):
    _inherit = 'mail.notification'

    notification_type = fields.Selection(selection_add=[('whatsapp', 'WhatsApp')])

class Followers(models.Model):
    _inherit = ['mail.followers']

    def _get_recipient_data(self, records, message_type, subtype_id, pids=None, cids=None):
        if message_type == 'whatsapp':
            if pids is None:
                sms_pids = records._sms_get_default_partners().ids
            else:
                sms_pids = pids
            res = super(Followers, self)._get_recipient_data(records, message_type, subtype_id, pids=pids, cids=cids)
            new_res = []
            for pid, cid, pactive, pshare, ctype, notif, groups in res:
                if pid and pid in sms_pids:
                    notif = 'whatsapp'
                new_res.append((pid, cid, pactive, pshare, ctype, notif, groups))
            return new_res
        else:
            return super(Followers, self)._get_recipient_data(records, message_type, subtype_id, pids=pids, cids=cids)


class MailMessage(models.Model):
    """ Override MailMessage class in order to add a new type: SMS messages.
    Those messages comes with their own notification method, using SMS
    gateway. """
    _inherit = 'mail.message'

    message_type = fields.Selection(selection_add=[('whatsapp', 'WhatsApp')])

    def set_message_done(self):
        res = super(MailMessage, self).set_message_done()
        for mail in self:
            if mail.model == 'project.task':
                task = self.env[self.model].browse(self.res_id)
                task.write({'stage_id': self.env.ref('project.project_stage_data_2').id})
        return res

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        recipients_data = super(MailThread, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)
        self._notify_record_by_whatsapp(message, recipients_data, msg_vals=msg_vals, **kwargs)
        return recipients_data

    def _notify_record_by_whatsapp(self, message, recipients_data, msg_vals=False,
                              whatsapp_numbers=None, sms_pid_to_number=None,
                              check_existing=False, put_in_queue=False, **kwargs):


        return True

    def _message_whatsapp(self, body, subtype_id=False, partner_ids=False, number_field=False,
                     whatsapp_numbers=None, sms_pid_to_number=None, **kwargs):
        """ Main method to post a message on a record using SMS-based notification
        method.

        :param body: content of SMS;
        :param subtype_id: mail.message.subtype used in mail.message associated
          to the sms notification process;
        :param partner_ids: if set is a record set of partners to notify;
        :param number_field: if set is a name of field to use on current record
          to compute a number to notify;
        :param sms_numbers: see ``_notify_record_by_sms``;
        :param sms_pid_to_number: see ``_notify_record_by_sms``;
        """
        return