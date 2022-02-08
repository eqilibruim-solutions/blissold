# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class Menu(models.Model):
    _inherit = "website.menu"
    icon = fields.Char('Menu Icon')
