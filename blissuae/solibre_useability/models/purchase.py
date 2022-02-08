from odoo import models, fields, api, exceptions, _
from odoo.tools import float_is_zero
from itertools import groupby

import logging

_logger = logging.getLogger(__name__)



class ShippingState(models.Model):
    _name = 'shipping.state'
    _description = 'Shipping State'

    name = fields.Char(string="State")

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    payment_id = fields.Many2one(string="Payment", comodel_name="account.payment")
    requisition_manager_user_id = fields.Many2one(string="Request approved by",
                                                  comodel_name="res.users",
                                                  related="requisition_id.manager_user_id")
    approver_id = fields.Many2one(string="Approved by", comodel_name="res.users", track_visibility='always')
    weight = fields.Float(string="Weight", compute="get_weight")
    price_override = fields.Float(string="Manual Total")
    shipping_state = fields.Many2one(string="Shipping Status", comodel_name="shipping.state")
    shipping_edd = fields.Date(string="Expected Date")
    tracking_number = fields.Char(string="Tracking number")
    tracking_url = fields.Char(string="Tracking URL")
    tracking_partner_id = fields.Many2one(string="Tacking Partner", comodel_name="res.partner")
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Analytic Account')
    requisition_line_id = fields.Many2one(string="Reuisition line", comodel_name="purchase.requisition.line")
    tracking_id = fields.Many2one(string="Shipment tracking", comodel_name="purchase.tracking")

    @api.onchange('requisition_id')
    def set_analytic_id(self):
        if self.requisition_id:
            self.analytic_account_id = self.requisition_id.account_analytic_id.id


    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        res = super(PurchaseOrder, self)._onchange_requisition_id()

        if self.requisition_id:
            self.analytic_account_id = self.requisition_id.account_analytic_id.id
            for line in self.order_line.filtered(lambda l:l.product_id.type == 'service'):
                line.account_analytic_id = self.analytic_account_id.id
        return res

    @api.onchange('amount_total')
    def set_manual_total(self):
        for po in self:
            if po.amount_total > 0:
                po.price_override = po.amount_total

    def get_weight(self):
        weight = 0
        for line in self.order_line:
            weight += line.product_id.weight * line.product_qty
        self.weight = weight 



    def write(self, vals):
        result = super(PurchaseOrder, self).write(vals)
        if self.state in ('sent','to approve','purchase','done') and self.requisition_id:
            self.requisition_id.order_state = self.state
        return result

    def _send_order_confirmation_mail(self):
        template_id = self.env.ref('purchase.email_template_edi_purchase_done')
        if template_id:
            for order in self:
                if order.partner_id.email:
                    # order = order.with_user(order.user_id.id)
                    order.with_context(force_send=True).message_post_with_template(template_id.id, composition_mode='comment', email_layout_xmlid="mail.mail_notification_paynow")


    def _create_picking(self):
        for order in self:
            new_product = self.env['product.product'].search([('default_code', '=like', 'NEW_%')])
            for line in order.order_line:
                if line.product_id in new_product:
                    created_product = line.product_id.copy({'name': line.name})
                    line.product_id = created_product.id
                    for req_line in order.requisition_id.line_ids.filtered(lambda l:l.name==line.name):
                        req_line.product_id = created_product.id
                        if order.requisition_id.categ_id:
                            created_product.categ_id = order.requisition_id.categ_id.id
        super(PurchaseOrder, self)._create_picking()


    def button_approve(self, force=False):
        res = super(PurchaseOrder, self).button_approve()
        if self.requisition_id and self.requisition_id.manager_user_id:
            self.message_subscribe(self.requisition_id.manager_user_id.partner_id.ids)
        self.activity_feedback(['solibre_useability.mail_act_purchase_approval_request'])
        self.write({'approver_id': self.env.user.id})
        self._send_order_confirmation_mail()
        return res

    def button_confirm(self):
        for po in self:
            if not self.user_has_groups('purchase.group_purchase_manager'):
                if po.product_id.categ_id.user_id:
                    approver = po.product_id.categ_id.user_id
                else:
                    approver = po.company_id.purchase_approver_id
                if approver:
                    note = "Request for approval %s" % po.name
                    self.activity_schedule('solibre_useability.mail_act_purchase_approval_request',note=note ,user_id=approver.id)
            res = super(PurchaseOrder, self).button_confirm()
            if po.requisition_id and po.requisition_id.type_id.auto_approve:
                _logger.info("Auto Approving")
                po.button_approve()
        return True

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal = self.env['account.move'].with_context(force_company=self.company_id.id, default_type='in_invoice')._get_default_journal()
        if not journal:
            raise exceptions.UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        invoice_vals = {
            'type': 'in_invoice',
            'currency_id': self.currency_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'partner_id': self.partner_id.id,
            'ref': self.partner_ref,
            'partner_shipping_id': self.partner_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_id.property_account_position_id.id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'company_id': self.company_id.id,
            'invoice_line_ids': [],
        }
        return invoice_vals

    def create_invoices(self):
        return self._create_invoices()

    def _create_invoices(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Create invoices.
        invoice_vals_list = []
        for order in self:
            pending_section = None

            # Invoice values.
            invoice_vals = order._prepare_invoice()

            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                if float_is_zero(qty_to_invoice, precision_digits=precision):
                    continue
                if qty_to_invoice > 0 or (qty_to_invoice < 0 and final):
                    if pending_section:
                        invoice_vals['invoice_line_ids'].append((0, 0, pending_section._prepare_invoice_line()))
                        pending_section = None
                    invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_invoice_line()))

            if not invoice_vals['invoice_line_ids']:
                raise exceptions.UserError(_('There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise exceptions.UserError(_(
                'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (x.get('partner_id'), x.get('currency_id'))):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    # payment_refs.add(invoice_vals['invoice_payment_ref'])
                    refs.add(invoice_vals['ref'])
                if refs:
                    try:
                        ref_invoice_vals.update({
                            'ref': ', '.join(refs),
                            # 'invoice_payment_ref': len(payment_refs) == 1 and payment_refs.pop() or False,
                        })
                    except:
                        _logger.info(refs)
                if origins:
                    try:
                        ref_invoice_vals.update({
                            'invoice_origin': ', '.join(origins),
                            # 'invoice_payment_ref': len(payment_refs) == 1 and payment_refs.pop() or False,
                        })
                    except:
                        _logger.info(origins)

                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        #_logger.info(invoice_vals_list)
        moves = self.env['account.move'].with_context(default_type='in_invoice', default_company_id=self.company_id.id).create(invoice_vals_list)
        _logger.info(moves.company_id.name)
        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id
            )
        return moves


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    is_downpayment = fields.Boolean(string="Is a down payment")
    employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee")


    def _prepare_invoice_line(self):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        return {
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.product_uom_qty - self.qty_invoiced,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.taxes_id.ids)],
            'analytic_account_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'purchase_line_id': self.id,
        }

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"

    def _create_invoice(self, order, so_line, amount):
        return

    def create_invoices(self):
        return
        
class PurchaseTracking(models.Model):
    _name = 'purchase.tracking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Purchase Tracking'

    name = fields.Char(string="Reference")
    date = fields.Date(string="Date")
    purchase_ids = fields.Many2many("purchase.order",string="Purchase orders")
    state = fields.Many2one(string="State", comodel_name="shipping.state")

    @api.onchange('state')
    def set_po_state(self):
        self.ensure_one()
        self.purchase_ids.write({'shipping_state':self.state.id})

