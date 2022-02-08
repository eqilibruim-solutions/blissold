from odoo import models, fields, api, exceptions, _
import csv
import base64
from io import StringIO
from datetime import datetime
import logging
from odoo.tests import Form
from xml.dom import minidom

_logger = logging.getLogger(__name__)


class SaleOrderImport(models.TransientModel):
    _name = 'sale.order.import'
    _description = 'Sale Order Import'

    data_file = fields.Binary(string="Lead CSV File")
    data_file_design2020 = fields.Binary(string="Lead Design2020 XML File")
    partner_id = fields.Many2one(string="Partner", comodel_name="res.partner")


    def load_so(self):
        if self.data_file:
            return self.load_so_csv()
        elif self.data_file_design2020:
            return self.load_so_design2020()
        return False

    def load_so_design2020(self):
        return




    def load_so_csv(self):
        return
