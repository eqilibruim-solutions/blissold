# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)


class StorageLocation(models.Model):
    _name = 'storage.location'
    _description = 'Storage Location'

    name = fields.Char(string="Storage Location", required=True)
    loc_x = fields.Char(string="X-Axis")
    loc_y = fields.Char(string="Y-Axis")
    loc_z = fields.Char(string="Y-Axis")

    @api.depends('name', 'loc_x', 'loc_y', 'loc_z',)
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.loc_x:
              name = name + record.loc_x
            if record.loc_y:
              name = name + record.loc_y
            if record.loc_z:
              name = name + record.loc_z
            res.append((record.id, name))
        return res

class StockLocalisation(models.Model):
    _name = 'stock.localisation'
    _description = 'Product Location'

    name = fields.Many2one(string="Product",
                           comodel_name="product.product",
                           required="True")
    product_tmpl_id = fields.Many2one(string="Product",
                                      comodel_name="product.template",
                                      related="name.product_tmpl_id")
    qty_available = fields.Float(string="Available quantity", related="product_tmpl_id.qty_available")
    virtual_available = fields.Float(string="Forecasted quantity", related="product_tmpl_id.virtual_available")
    storage_location_id = fields.Many2one(string="Storage Location",
                                  comodel_name="storage.location")
    location_id = fields.Many2one(string="Location",
                                  comodel_name="stock.location",
                                  default=lambda self: self.env['stock.location'].search([('usage', '=', 'internal')],limit=1).id,
                                  domain=[('usage', '=', 'internal')])

    _sql_constraints = [
        ('name_company_uniq', 'unique(name,storage_location_id,location_id)', 'Product and Localisation has to be unique to Location!')
    ]

    @api.onchange('product_tmpl_id')
    def set_product(self):
        for loc in self:
            loc.name = loc.product_tmpl_id.product_variant_id   

class stock_move(models.Model):

    _inherit = 'stock.move'

    localisation_id = fields.Many2one(string="Localisation", comodel_name="stock.localisation", compute="check_localisation")

    @api.depends('product_id', 'location_id')
    def check_localisation(self):
        for operation in self:
            localisation = False
            if operation.product_id and operation.location_id:
                localisation = self.env['stock.localisation'].search([('name', '=', operation.product_id.id),
                                                                      ('location_id', '=', operation.location_id.id)],limit=1)
                localisation = localisation.id
            operation.localisation_id = localisation

