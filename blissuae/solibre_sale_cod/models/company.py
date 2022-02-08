from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    auto_signup = fields.Boolean(string="Auto Signup")