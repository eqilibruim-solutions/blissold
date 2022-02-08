from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    zone_ids = fields.Many2many(string="Zones", comodel_name="delivery.zone")

    def _match_address(self, partner):
        self.ensure_one()
        res = super(DeliveryCarrier, self)._match_address(partner)
        if self.zone_ids and partner.delivery_zone_id in self.zone_ids:
            return True
        elif not self.zone_ids:
            return res