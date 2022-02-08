from odoo import models, fields, api, exceptions, _
from odoo.http import request

import logging

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    def _prepare_sale_order_values(self, partner, pricelist):
        self.ensure_one()
        values = super(Website, self)._prepare_sale_order_values(partner, pricelist)
        delivery_address = request.env['res.partner'].browse(values.get('partner_shipping_id'))
        delivery_zone_id = delivery_address.city_id and delivery_address.city_id.zone_id
        if delivery_zone_id and delivery_zone_id.team_id:
            salesteam_id = delivery_zone_id.sudo().team_id
            values.update({'team_id':salesteam_id.id})
            if salesteam_id and salesteam_id.user_id:
                values.update({'user_id': salesteam_id.user_id.id})
        return values