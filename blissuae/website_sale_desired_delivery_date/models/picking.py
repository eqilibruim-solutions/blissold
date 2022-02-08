from odoo import models, fields, api, exceptions, _

import logging
import re

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    gift_message = fields.Text(string="Gift Message", compute="get_delivery_instruction")
    

    def is_arabic(self):
        self.ensure_one()
        if re.findall(r'[\u0600-\u06FF]+',self.gift_message):
            return True
        else:
            return False

    @api.depends('sale_id','purchase_id')
    def get_delivery_instruction(self):
        for picking in self:
            sale_id = self.env['sale.order'].search([('name', '=', picking.origin)])
            if sale_id:
                picking.note = sale_id.delivery_note
                picking.gift_message = sale_id.gift_message
            else:
                picking.note = False
                picking.gift_message = False
        return True