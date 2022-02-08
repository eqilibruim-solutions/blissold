from odoo import models, fields, api, _

import urllib
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class DeliveryTimeSlot(models.Model):
    _name = 'delivery.time.slot'
    _description = 'Delivery Time Slot'

    name = fields.Char(string="Time Slot")

class DeliveryArea(models.Model):
    _name = 'delivery.area'
    _description = 'Delivery Area'
    _order = 'name'

    name = fields.Char(string="Name")
    zone_id = fields.Many2one(string="Zone", comodel_name="delivery.zone")
    state_id = fields.Many2one(string="State", comodel_name="res.country.state")
    sorting = fields.Char(string="Sorting Number")
    center_longitude = fields.Float('Center Longitude', digits=(16, 5))
    center_latitude = fields.Float('Center Latitude', digits=(16, 5))


class DeliveryZoneScheduleLine(models.Model):
    _name = 'delivery.zone.schedule.line'
    _description = 'Zone Schedule Line'

    name = fields.Selection([
            ('MO', 'Monday'),
            ('TU', 'Tuesday'),
            ('WE', 'Wednesday'),
            ('TH', 'Thursday'),
            ('FR', 'Friday'),
            ('SA', 'Saturday'),
            ('SU', 'Sunday')
        ], string='Day', required="1")
    time_slot_ids = fields.Many2many(string="Time slot", comodel_name="delivery.time.slot", required="1")
    schedule_id = fields.Many2one(string="Schedule", comodel_name="delivery.zone.schedule")

class DeliveryZoneSchedule(models.Model):
    _name = 'delivery.zone.schedule'
    _description = 'Zone Schedule'

    name = fields.Many2one(string="Zone", comodel_name="delivery.zone")
    schedule_line_ids = fields.One2many(string="Schedule lines", comodel_name="delivery.zone.schedule.line", inverse_name="schedule_id")

class DeliveryZone(models.Model):
    _name = 'delivery.zone'
    _description = 'Delivery Zone'
    _order = 'name'
    name = fields.Char(string="Zone name")
    city_id = fields.Many2one(string="City", comodel_name="res.city")
    country_id = fields.Many2one(string="Country", comodel_name="res.country")
    area_ids = fields.One2many(string="Areas", comodel_name="delivery.area", inverse_name="zone_id")
    user_ids = fields.Many2many(string="Driver", comodel_name="res.users")
    partner_id = fields.Many2one(string="Partner", comodel_name="res.partner")
    company_id = fields.Many2one(string="Company", comodel_name="res.company")

    @api.depends('name', 'city_id', 'country_id')
    def name_get(self):
        result = []
        for zone in self:
            name = zone.name
            if zone.city_id:
                name += ' - %s'%zone.city_id.name
            if zone.country_id:
                name += ' - %s'%zone.country_id.code
            result.append((zone.id, name))
        return result


    