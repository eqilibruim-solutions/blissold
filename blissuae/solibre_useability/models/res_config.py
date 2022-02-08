from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_shortname = fields.Char(related='company_id.shortname', readonly=False)
    sale_auto_invoice = fields.Boolean(related='company_id.sale_auto_invoice', readonly=False)
    sale_auto_pay = fields.Boolean(related='company_id.sale_auto_pay', readonly=False)
    purchase_approver_id = fields.Many2one("res.users", "Purchase approver",
                                           related="company_id.purchase_approver_id",
                                           readonly=False)
    sale_approver_id = fields.Many2one("res.users", "Sale approver",
                                           related="company_id.sale_approver_id",
                                           readonly=False)
    sale_approval_amount = fields.Float(string="Approval limit",
    									related="company_id.sale_approval_amount",
    									readonly=False)