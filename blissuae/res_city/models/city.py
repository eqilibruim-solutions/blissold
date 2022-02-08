from odoo import models, fields, api, _

import urllib
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class res_city(models.Model):

    _name = 'res.city'
    _inherits = ''
    _description = 'Cities'

    name = fields.Char(string="Name", required=True, translate=True)
    country_id = fields.Many2one(string="Country", comodel_name="res.country")

    def name_get(self):
        res = []
        for city in self:
            if city.country_id:
                name = "%s (%s)" % (city.name, city.country_id.code)
            else:
                name = city.name
            res += [(city.id, name)]
        return res
