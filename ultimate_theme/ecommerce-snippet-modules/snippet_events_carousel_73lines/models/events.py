# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from odoo import models


class WebsiteEvents(models.Model):
    _name = 'event.event'
    _inherit = ['event.event', 'carousel.slider']
