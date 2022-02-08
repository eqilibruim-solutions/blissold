from odoo import models, fields, api, exceptions, _
import csv
import base64
from io import StringIO
from datetime import datetime
import logging
from odoo.tests import Form
import gspread
from oauth2client.service_account import ServiceAccountCredentials

_logger = logging.getLogger(__name__)
    

class PurchaseOrderImport(models.TransientModel):
    _name = 'purchase.order.import'
    _description = 'Purchase Order Import'

    data_file = fields.Binary(string="Lead CSV File")
    partner_id = fields.Many2one(string="Partner", comodel_name="res.partner")
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency")

    def create_po(self, fields, data):
        return

    def load_supplier_invoices(self):
        return
