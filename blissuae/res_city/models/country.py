from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)

class ResCountry(models.Model):
    _inherit = 'res.country'

    delivery_zone_id = fields.Many2one(string="Zone", comodel_name="delivery.zone")

    # def get_website_sale_countries(self, mode='billing'):
    #     res = super(ResCountry, self).get_website_sale_countries(mode=mode)
    #     countries = self.env['res.country']

    #     delivery_carriers = self.env['delivery.carrier'].sudo().search([('website_published', '=', True)])
    #     for carrier in delivery_carriers:
    #         if not carrier.country_ids and not carrier.state_ids:
    #             countries = res
    #             break
    #         countries |= carrier.country_ids

    #     res = res & countries
    #     return res