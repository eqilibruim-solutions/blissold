from odoo import models, fields, api, exceptions, _
import xmlrpc.client 
import logging
import requests

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    sale_auto_invoice = fields.Boolean("Auto invoice")
    sale_auto_pay = fields.Boolean("Prompt Payment", default=True)
    purchase_approver_id = fields.Many2one("res.users", string="PO Approver")
    sale_approver_id = fields.Many2one("res.users", string="SO Approver")
    sale_approval_amount = fields.Float(string="SO Approval amount")
    limit_product_to_pricelist = fields.Float(string="Limit product to pricelist")
    shortname = fields.Char(string="Short name")

    @api.model
    def get_database_validity(self):
        return

    @api.model
    def sync_odoo_images(self, url, db, username, password, model, fields, domain, new_model=False, new_fields=False, raise_error=False, bulk=False):
        return True


    @api.model
    def sync_odoo_data(self, url, db, username, password, model, fields, domain, new_model=False, new_fields=False, raise_error=False, bulk=False):

        return True

    @api.model
    def sync_odoo_products(self, url, db, username, password, model, fields, domain, new_model=False, new_fields=False, raise_error=False, bulk=False):

        return True

