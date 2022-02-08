# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError

import csv
import base64
import io
import datetime

import logging
_logger = logging.getLogger(__name__)


class sa_tax_report_line(models.Model):

    _name = 'tax.report.sa.line'
    _description = 'Tax report line'
    _rec_name = 'report_id'

    report_id = fields.Many2one(string="Report", comodel_name="account.tax.report.sa")
    tax_id = fields.Many2one(string="Tax", comodel_name="account.tax")
    amount = fields.Float(string="Amount")
    amount_vat = fields.Float(string="VAT Amount")


class account_tax_report_sa(models.Model):

    _name = 'account.tax.report.sa'
    _description = 'VAT Report'
    _rec_name = 'date_start'

    @api.onchange('date_start','date_stop')
    def onchange_date(self):
        if self.tax_line_ids:
            self.tax_line_ids.unlink()
            self.update({
                    'vat_debit' : 0, 
                    'vat_credit' : 0, 
                    'vat_diff' : 0, })             

    def compute_tax(self):
        tax_obj = self.env['account.tax']
        return 


    date_start = fields.Date(string="VAT Period", required=True)
    date_stop = fields.Date(string="Vat period to", required=True)
    vat_debit = fields.Float(string="VAT Paid")
    vat_credit = fields.Float(string="VAT Received")
    vat_diff = fields.Float(string="VAT Difference")
    invoice_id = fields.Many2one(string="Payment Order", comodel_name="account.move")
    partner_id = fields.Many2one(string="Beneficiary", comodel_name="res.partner")
    tax_line_ids = fields.One2many(string="Tax Lines", comodel_name="tax.report.sa.line", inverse_name="report_id")
    company_id = fields.Many2one(string="Company", comodel_name="res.company",
                                 required=True, readonly=True,
                                 default=lambda self: self.env['res.company']._company_default_get())

    def write(self, vals):
        res = super(account_tax_report_sa, self).write(vals)
        if vals.get('tax_line_ids'):
            to_remove = self.env['tax.report.sa.line'].search([('report_id', '=', False)])
            to_remove.unlink()
        return res

    def open_vat_invoices(self):
        self.ensure_one()
        domain = [('date', '>=', self.date_start),
                  ('date', '<=', self.date_stop),
                  ('tax_line_id', '!=', False)]
        return {'name': _('VAT Entries'),
                'view_type': 'form',
                'view_mode': 'pivot,tree,form',
                'context': {'pivot_column_groupby': ['date:month'],
                            'group_by': ['account_id'],
                            'pivot_measures': ['tax_base_amount', 'debit', 'credit', 'balance']},
                'res_model': 'account.move.line',
                'domain': domain,
                'type': 'ir.actions.act_window'}

    def generate_move(self):
        return

    def create_tax_report(self):
        return
