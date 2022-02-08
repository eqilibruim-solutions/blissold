# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import hashlib
import urllib.parse as urlparse
from odoo import api, fields, models


class MailchimpSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'mailchimp.settings'
    _description = 'Mailchimp settings'

    mc_username = fields.Char(required=True)
    mc_apikey = fields.Char(required=True)
    mc_webhook_url = fields.Char(compute='_compute_webhook_url')
    import_shopify_order_status_ids = fields.Char(string="Shopify")
    
    @api.depends('mc_username')
    def _compute_webhook_url(self):
        return False
        base_url = urlparse.urlparse(
            self.env['ir.config_parameter'].get_param('web.base.url'),
        )
        for this in self:
            this.webhook_url = urlparse.urlunparse(
                base_url[:2].encode() + ('/mailchimp/%s' % self._get_webhook_key(),).encode() +
                base_url[3:].encode(),
            )

    
    def get_default_values(self, fields):
        get_param = self.env['ir.config_parameter'].get_param
        return {
            key: get_param('crm_mailchimp.%s' % key)
            for key in ('mc_username', 'mc_apikey')
        }

    
    def set_username(self):
        return self.env['ir.config_parameter'].set_param(
            'crm_mailchimp.username', self.mc_username,
        )

    
    def set_apikey(self):
        return self.env['ir.config_parameter'].set_param(
            'crm_mailchimp.apikey', self.mc_apikey,
        )

    
    def execute(self):
        result = super(MailchimpSettings, self).execute()
        if result:
            self.env['mailchimp.list']._read_from_mailchimp()
        return result

    @api.model
    def _get_webhook_key(self):
        return hashlib.sha1(
            self.env['ir.config_parameter'].get_param('database.secret') +
            self.env['ir.config_parameter'].get_param('web.base.url')
        ).hexdigest()
