from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)

class SaleOrderLimit(models.Model):
    _name = 'sale.order.limit'
    _description = 'Limit Orders per day'

    team_id = fields.Many2one('crm.team', string='Default Sales Team')
    date = fields.Date(string="Date")
    max_orders = fields.Float(string="Max. Orders", required=True)
    time_slot_ids = fields.Many2many(string="Time slot", comodel_name="delivery.time.slot", required=False)

    @api.model
    def get_orders(self, date):
        domain = [('pref_date', '=', date), ('state', 'in', ('sale', 'done'))]
        return self.env['sale.order'].sudo().search_count(domain)

    def max_orders_reached(self, date ,order, slot):
        return False
