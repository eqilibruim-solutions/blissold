# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    discount = fields.Float('Discount %', readonly=True)
    discount_amount = fields.Float('Discount Amount', readonly=True)

    def _select(self):
        sql = """,sum((line.price_unit * line.discount / 100.0 ) * line.quantity) as discount_amount,
        line.discount as discount"""
        return super(AccountInvoiceReport, self)._select() + sql

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", discount"