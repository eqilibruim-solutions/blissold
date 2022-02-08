from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_signup = fields.Boolean(related='company_id.auto_signup', readonly=False)