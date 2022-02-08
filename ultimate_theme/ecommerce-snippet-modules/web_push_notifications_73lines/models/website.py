# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class WebsiteOneSignal(models.Model):
    _inherit = 'website'

    onesignal_app_id = fields.Char(string='App Id')
    onesignal_safari_web_id = fields.Char(string='Safari Web Id')
    onesignal_site_name = fields.Char(string='WebSite Name')
    onesignal_site_short_name = fields.Char(string='WebSite Short Name')


class WebsiteConfigSettingsOneSignal(models.TransientModel):
    _inherit = 'res.config.settings'

    onesignal_app_id = fields.Char(string='App Id',
                                   related='website_id.onesignal_app_id')
    onesignal_safari_web_id = fields.Char(
        string='Safari Web Id', related='website_id.onesignal_safari_web_id')
    onesignal_site_name = fields.Char(string='WebSite Name',
                                      related='website_id.onesignal_site_name')
    onesignal_site_short_name = fields.Char(
        string='WebSite Short Name',
        related='website_id.onesignal_site_short_name')
