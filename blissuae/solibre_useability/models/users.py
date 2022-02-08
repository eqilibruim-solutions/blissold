from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    signature_image = fields.Binary(string="Signature")
    # warehouse_id = fields.Many2one(string="Default Warehouse", comodel_name="stock.warehouse")

    def get_current_company(self):
    	_logger.info(self.env.company)
    	return self.env.company

    