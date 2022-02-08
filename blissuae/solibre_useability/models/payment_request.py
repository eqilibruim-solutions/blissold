from odoo import models, fields, api, exceptions, _
import time
import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    sale_id = fields.Many2one(string="Sale Order", comodel_name="sale.order")
    purchase_id = fields.Many2one(string="Sale Order", comodel_name="sale.order")


class PaymentRequest(models.TransientModel):
    _name = 'payment.request'
    _description = 'Payment Payment'

    @api.model
    def _get_amount(self):
        for wiz in self:
            amount = 0
            record = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))
            if record:
                if record._name == 'purchase.requisition':
                    for line in record.line_ids:
                        amount += line.price_unit * line.product_qty
                elif record._name == 'purchase.order':
                    for line in record.order_line:
                        amount += line.price_unit * line.product_qty
                elif record._name == 'sale.order':
                    for line in record.order_line:
                        amount += line.price_unit * line.product_qty
                wiz.amount = amount
            return amount

    amount = fields.Float(string="Amount", default=_get_amount)
    ref = fields.Char(string="Reference")
    journal_id = fields.Many2one(string="Mode", comodel_name="account.journal", domain=[('type','in',('cash','bank'))])


    def payment_request(self):
        payment_obj = self.env['account.payment']
        for wiz in self:
            record = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))
            if record.currency_id == record.company_id.currency_id:
                currency_id = False
            else:
                currency_id = record.currency_id.id
            if not self.journal_id:
                journal_id = self.env['account.journal'].search([('type', '=', 'cash'),
                                                                 ('company_id','=',self.env.user.company_id.id),
                                                                 ('currency_id', '=', currency_id)], limit=1)
            else:
                journal_id = self.journal_id

            if not journal_id:
                raise exceptions.ValidationError("Payment journal not yet configured")

            if record._name == 'purchase.requisition':
                partner = record.vendor_id and record.vendor_id.id or record.user_id.partner_id.id
                payment_type = 'outbound'
                partner_type = 'supplier'
                payment_method_id = self.env.ref("account.account_payment_method_manual_out").id
            elif record._name == 'purchase.order':
                partner = record.partner_id.id
                payment_type = 'outbound'
                partner_type = 'supplier'
                payment_method_id = self.env.ref("account.account_payment_method_manual_out").id
            elif record._name == 'sale.order':
                partner = record.partner_id.id
                payment_type = 'inbound'
                partner_type = 'customer'
                payment_method_id = self.env.ref("account.account_payment_method_manual_in").id

            payment_data = {
                'payment_date': time.strftime('%Y-%m-%d'),
                'payment_type': payment_type,
                'amount': wiz.amount,
                'currency_id': record.currency_id.id,
                'journal_id': journal_id.id,
                'partner_type': partner_type,
                'partner_id': partner,
                'communication': "%s %s" % (record.name, wiz.ref or ''),
                'payment_method_id': payment_method_id}
            payment_id = payment_obj.create(payment_data)
            if record._name == 'sale.order':
                payment_id.sale_id = record.id
                payment_id.post()
            elif record._name == 'purchase.order':
                payment_id.purchase_id = record.id
            else:
                record.payment_id = payment_id.id

