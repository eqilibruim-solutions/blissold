# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import uuid

import logging

_logger = logging.getLogger(__name__)
    

def _get_document_types(self):
    return [(doc.model.model, doc.name) for doc in self.env['subscription.document'].search([], order='name')]


class SubscriptionDocument(models.Model):
    _name = "subscription.document"
    _description = "Subscription Document"

    name = fields.Char(required=True)
    active = fields.Boolean(help="If the active field is set to False, it will allow you to hide the subscription document without removing it.", default=True)
    model = fields.Many2one('ir.model', string="Object", required=True)
    field_ids = fields.One2many('subscription.document.fields', 'document_id', string='Fields', copy=True)


class SubscriptionDocumentFields(models.Model):
    _name = "subscription.document.fields"
    _description = "Subscription Document Fields"
    _rec_name = 'field'

    field = fields.Many2one('ir.model.fields', domain="[('model_id', '=', parent.model)]", required=True)
    value = fields.Selection([('false', 'False'), ('date', 'Current Date')], string='Default Value', help="Default value is considered for field when new document is generated.")
    document_id = fields.Many2one('subscription.document', string='Subscription Document', ondelete='cascade')


class Subscription(models.Model):
    _name = "subscription.subscription"
    _inherit = ['mail.thread']
    _description = "Subscription"

    uuid = fields.Char('Account UUID', default=lambda s: uuid.uuid4(), copy=False, required=True)
    name = fields.Char(required=True)
    active = fields.Boolean(help="If the active field is set to False, it will allow you to hide the subscription without removing it.", default=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    notes = fields.Text(string='Interal Notes')
    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user)
    interval_number = fields.Integer(string='Interval Qty', default=1)
    interval_type = fields.Selection([('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')], string='Interval Unit', default='months')
    exec_init = fields.Integer(string='Number of Documents')
    date_init = fields.Datetime(string='First Date', default=fields.Datetime.now)
    state = fields.Selection([('draft', 'Draft'), ('running', 'Running'), ('done', 'Done')], string='Status', copy=False, default='draft')
    doc_source = fields.Reference(selection=_get_document_types, string='Source Document', required=True, help="User can choose the source document on which he wants to create documents")
    doc_lines = fields.One2many('subscription.subscription.history', 'subscription_id', string='Documents created', readonly=True)
    cron_id = fields.Many2one('ir.cron', string='Cron Job', help="Scheduler which runs on subscription", states={'running': [('readonly', True)], 'done': [('readonly', True)]})
    note = fields.Text(string='Notes', help="Description or Summary of Subscription")

    @api.model
    def _auto_end(self):
        super(Subscription, self)._auto_end()
        # drop the FK from subscription to ir.cron, as it would cause deadlocks
        # during cron job execution. When model_copy() tries to write() on the subscription,
        # it has to wait for an ExclusiveLock on the cron job record, but the latter
        # is locked by the cron system for the duration of the job!
        # FIXME: the subscription module should be reviewed to simplify the scheduling process
        #        and to use a unique cron job for all subscriptions, so that it never needs to
        #        be updated during its execution.
        self.env.cr.execute("ALTER TABLE %s DROP CONSTRAINT %s" % (self._table, '%s_cron_id_fkey' % self._table))

    def set_process(self):
        for subscription in self:
            cron_data = {
                
            }
            cron = self.env['ir.cron'].sudo().create(cron_data)
            subscription.write({'cron_id': cron.id, 'state': 'running'})

    @api.model
    def _cron_model_copy(self, ids):
        self.browse(ids).model_copy()

    def model_copy(self):
        for subscription in self.filtered(lambda sub: sub.cron_id):
            if not subscription.doc_source.exists():
                raise UserError(_('Please provide another source document.\nThis one does not exist!'))

            default = {'state': 'draft'}
            documents = self.env['subscription.document'].search([('model.model', '=', subscription.doc_source._name)], limit=1)
            fieldnames = dict((f.field.name, f.value == 'date' and fields.Date.today() or False)
                               for f in documents.field_ids)
            default.update(fieldnames)

            # if there was only one remaining document to generate
            # the subscription is over and we mark it as being done
            if subscription.cron_id.numbercall == 1:
                subscription.write({'state': 'done'})
            else:
                subscription.write({'state': 'running'})
            copied_doc = subscription.doc_source.copy(default)
            self.env['subscription.subscription.history'].create({
                'subscription_id': subscription.id,
                'date': fields.Datetime.now(),
                'document_id': '%s,%s' % (subscription.doc_source._name, copied_doc.id)})

    def unlink(self):
        if any(self.filtered(lambda s: s.state == "running")):
            raise UserError(_('You cannot delete an active subscription!'))
        return super(Subscription, self).unlink()

    def set_done(self):
        self.mapped('cron_id').write({'active': False})
        self.pause_subscription_send()
        self.write({'state': 'done'})

    def set_draft(self):
        self.write({'state': 'draft'})

    def compute_subscription(self, obj):
        for invoice in obj:
            template = '%s,%s' % (invoice._name, invoice.id)
            subs = self.env['subscription.subscription'].search([('doc_source', '=', template)])
            invoice.subscription_count = len(subs)

    def action_view_subscription(self, obj):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('solibre_useability.action_subscription_form')
        result = action.read()[0]
        template = '%s,%s' % (obj._name, obj.id)
        context = dict(self.env.context or {})
        context['default_doc_source'] = template
        result['context'] = context
        result['domain'] = "[('doc_source','=','%s')]" % template
        result['views'] = [(False,'form')]
        subscription_document = self.env['subscription.document'].search([('model.model', '=', obj._name)])
        if not subscription_document:
            model = self.env['ir.model'].search([('model','=', obj._name)])
            subscription_document = self.env['subscription.document'].create({'name':model.name,
                                                                              'model': model.id})
        subscription = self.env['subscription.subscription'].search([('doc_source', '=', template)])
        if subscription:
            res = self.env.ref('subscripton.view_subscription_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = subscription.id
        return result

    def action_create_subscription(self, obj, interval_number, interval_type, start_date, count):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        subscription_obj = self.env['subscription.subscription']
        template = '%s,%s' % (obj._name, obj.id)
        subscription_document = self.env['subscription.document'].search([('model.model', '=', obj._name)])
        if not subscription_document:
            model = self.env['ir.model'].search([('model','=', obj._name)])
            subscription_document = self.env['subscription.document'].create({'name':model.name,
                                                                              'model': model.id})
        subscription = subscription_obj.search([('doc_source', '=', template)])
        if not subscription:
            data = {'doc_source': template,
                    'name': obj.name,
                    'partner_id': obj.partner_id.id,
                    'interval_number': interval_number,
                    'interval_type': interval_type,
                    'date_init': start_date,
                    'exec_init': count,
                    }
            subscription = subscription_obj.create(data)
            subscription.set_process()
        return subscription.id

    def action_subscription_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('letscook_custom', 'email_template_edi_subscription')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'subscription.subscription',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_light",
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


    def force_subscription_send(self):
        for order in self:
            email_act = order.action_subscription_send()
            if email_act and email_act.get('context'):
                email_ctx = email_act['context']
                email_ctx.update(default_email_from=order.doc_source.company_id.email)
                order.with_context(email_ctx).message_post_with_template(email_ctx.get('default_template_id'), custom_layout='mail.mail_notification_light')
        return True

    def action_subscription_pause_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('letscook_custom', 'email_template_pause_subscription')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'subscription.subscription',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_light",
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


    def pause_subscription_send(self):
        for order in self:
            email_act = order.action_subscription_pause_send()
            if email_act and email_act.get('context'):
                email_ctx = email_act['context']
                email_ctx.update(default_email_from=order.doc_source.company_id.email)
                order.with_context(email_ctx).message_post_with_template(email_ctx.get('default_template_id'), custom_layout='mail.mail_notification_light')
        return True

class SubscriptionHistory(models.Model):
    _name = "subscription.subscription.history"
    _description = "Subscription history"
    _rec_name = 'date'

    date = fields.Datetime()
    subscription_id = fields.Many2one('subscription.subscription', string='Subscription', ondelete='cascade')
    document_id = fields.Reference(selection=_get_document_types, string='Source Document', required=True)
