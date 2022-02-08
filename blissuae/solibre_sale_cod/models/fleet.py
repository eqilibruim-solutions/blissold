from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    city_id = fields.Many2one(string="Area", comodel_name="delivery.area")
    zone_ids = fields.Many2many(string="Zones", comodel_name="delivery.zone")
    multiple_drivers = fields.Boolean(string="Multiple Drivers", help="Allows selecting any driver during scheduling")
