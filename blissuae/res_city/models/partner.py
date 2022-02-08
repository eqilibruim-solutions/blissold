from odoo import models, fields, api, _

import urllib
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class res_partner(models.Model):

    _inherit = 'res.partner'

    #city_id = fields.Many2one(string="City", comodel_name="res.city")
    city_id = fields.Many2one(string="Delivery Zone", comodel_name="delivery.area")
    delivery_zone_id = fields.Many2one(string="Delivery Zone", 
                                       comodel_name="delivery.zone", 
                                       domain="[('city_id','=',city_id)]",
                                       compute="get_zone")
    delivery_area_id = fields.Many2one(string="Delivery Zone", comodel_name="delivery.area")

    city = fields.Char(string="City", related="city_id.name", store=True)
    location_url = fields.Char(string="Location")

    @api.onchange('city_id')
    def change_city(self):
        for partner in self:
            partner.city = partner.city_id.name

    @api.depends('city_id')
    @api.onchange('city_id')
    def get_zone(self):
        for partner in self:
            partner.delivery_zone_id = partner.city_id.zone_id.id



    def _display_address(self, without_company=False):

        '''
        The purpose of this function is to build and return an address formatted accordi$
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the$
            if not country is specified)
        :rtype: string
        '''
        # get the information that will be injected into the display format
        # get the address format
        address_format = self._get_address_format()
        args = {
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'city_name': self.city_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self._get_country_name(),
            'company_name': self.commercial_company_name or '',
        }
        for field in self._formatting_address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args