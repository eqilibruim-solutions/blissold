from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_cod = fields.Boolean(string="Cash on delivery?")
    cash_user_id = fields.Many2one(string="Allowed users", comodel_name="res.users")
    driver_id = fields.Many2one(string="Associated Driver", comodel_name="res.partner")