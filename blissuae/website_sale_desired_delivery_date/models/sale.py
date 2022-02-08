from odoo import models, fields, api, exceptions, _

import logging
import re

_logger = logging.getLogger(__name__)

class CalendarDay(models.Model):
    _name = 'calendar.day'
    _description = 'Calendar Day'

    name = fields.Char(string="Day")

class DeliveryTimeSlot(models.Model):
    _name = 'delivery.time.slot'
    _description = 'Delivery Time Slot'

    name = fields.Char(string="Time Slot", required=True)
    hour = fields.Float(string="Hour of the day", required=True)
    days = fields.Many2many("calendar.day",string="Days")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_note = fields.Text(string="Delivery note")
    gift_message = fields.Text(string="Gift Message")
    pref_date = fields.Date(string="Delivery date")
    time_slot = fields.Many2one(string="Delivery time slot", comodel_name="delivery.time.slot")

    def is_arabic(self):
        self.ensure_one()
        if re.findall(r'[\u0600-\u06FF]+',self.gift_message):
            return True
        else:
            return False