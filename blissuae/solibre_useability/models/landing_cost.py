from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)


class AccountLandingCost(models.Model):
    _name = 'account.landing.cost'
    _description = 'Landing Cost'

    state = fields.Selection(string="State", selection=[('draft','Draft'),('done','Done')])
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    date = fields.Date(string="Date")
    main_invoice_ids = fields.One2many(string="Purchase Invoices", 
                                       comodel_name="account.move", 
                                       inverse_name="landing_cost_main_id",
                                       domain="[('landing_cost_main_id','=',False),('type','=','in_invoice')]"
                                       )
    add_invoice_ids = fields.One2many(string="Additional Invoices",
                                      comodel_name="account.move",
                                      inverse_name="landing_cost_add_id",
                                      domain="[('landing_cost_main_id','=',False),('type','=','in_invoice')]"
                                      )

    @api.model
    def create(self, vals):
        return