from odoo import models, fields, api, exceptions, _
import json

import logging

_logger = logging.getLogger(__name__)


    
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    city_id = fields.Many2one(string="City", comodel_name="delivery.area", related="partner_id.city_id", store=True)
    delivery_zone_id = fields.Many2one(string="Zone", comodel_name="delivery.zone", related="sale_id.delivery_zone_id", store=True)
    pickup_location_id = fields.Many2one(string="Pickup Location", comodel_name="res.company", related="sale_id.pickup_location_id", store=True)
    mobile = fields.Char(string="Mobile", related="partner_id.mobile")
    accepted_by = fields.Many2one(string="Accepted by", comodel_name="res.users")
    prepared_by = fields.Many2one(string="Prepared by", comodel_name="res.users")
    workorder_status = fields.Char(string="Work order status")
    pref_date = fields.Date(string="Delivery Date", compute="get_delivery_date", store=True)
    time_slot = fields.Many2one(string="Time slot", comodel_name="delivery.time.slot", compute="get_delivery_date", store=True)
    products_json = fields.Text(string="Products JSON", compute="_get_products")
    team_id = fields.Many2one(string="Sales Team", comodel_name="crm.team", related="sale_id.team_id", store=True)

    def _get_products(self):
        for picking in self:
            data = {}
            for line in picking.sale_id.order_line.filtered(lambda l:l.product_id.type=='product'):
                data[line.product_id.name] = line.product_uom_qty
            picking.products_json = json.dumps(data)

    @api.depends('origin', 'sale_id')
    @api.onchange('origin', 'sale_id')
    def get_delivery_date(self):
        for picking in self:
            sale = picking.sale_id
            if not sale:
                sale = self.env['sale.order'].sudo().search([('name','=',picking.origin)], limit=1)
            if sale.pref_date:
                picking.pref_date = sale.pref_date
                picking.time_slot = sale.time_slot.id
            else:
                picking.pref_date = False
                picking.time_slot = False

    def update_delivery_zone(self):
        for picking in self:
            picking.sale_id.get_delivery_zone()

    def set_accepted(self):
        for picking in self:
            picking.accepted_by = self.env.user.id
            picking.sale_id.set_accepted()


    def set_prepared(self):
        for picking in self:
            picking.prepared_by = self.env.user
            picking.sale_id.set_prepared()


class StockMove(models.Model):
    _inherit = 'stock.move' 

    categ_id = fields.Many2one(string="Category", comodel_name="product.category", related="product_id.categ_id", store=True)
    order_id = fields.Many2one(string="Order", comodel_name="sale.order", related="sale_line_id.order_id", store=True)