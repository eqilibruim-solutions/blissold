from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    pref_date = fields.Date(string="Delivery Date", compute="get_delivery_date", store=True)

    def get_mrp_stock_available(self):
        for mrp in self:
            mrp.move_raw_ids.get_mrp_available_stock()

    def get_delivery_date(self):
        for mo in self:
            sale = self.env['sale.order'].sudo().search([('name','=',mo.origin)], limit=1)
            if sale.pref_date:
                mo.pref_date = sale.pref_date
            else:
                mo.pref_date = False

    def action_confirm(self):
        self._check_company()
        for production in self:
            production._onchange_move_raw()
            if not production.move_raw_ids:
                return True
        return super(MrpProduction, self).action_confirm()


