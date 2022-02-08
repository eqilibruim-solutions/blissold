from odoo import models, fields, api, exceptions, _
from datetime import datetime, timedelta
import logging
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)


class SolRequisitionLine(models.TransientModel):
    _name = 'sol.requisition.line'
    _description = 'Sol Requisition Lines'

    product_id = fields.Many2one(string="Product", comodel_name="product.product")
    partner_ids = fields.Many2many(string="Partners", comodel_name="res.partner")
    requisition_id = fields.Many2one(string="Req", comodel_name="sol.requisition")
    qty = fields.Float(string="Quantity")

class SaleOrderLineRequisition(models.TransientModel):
    _name = 'sol.requisition'
    _description = 'Sale Order Line Requisition'

    order_id = fields.Many2one(string="Sale Order", comodel_name="sale.order")
    order_line_id = fields.Many2one(string="Order Line", comodel_name="sale.order.line")
    line_ids = fields.One2many(string="sol.requisition.line", comodel_name="sol.requisition.line", inverse_name="requisition_id")

    @api.onchange('order_line_id')
    def get_products(self):
        products = []
        current_section = False
        for line in self.order_line_id.order_id.order_line:
            if line.display_type == 'line_section':
                if line.id == self.order_line_id.id:
                    current_section = True
                else:
                    current_section = False
            if current_section and line.product_id:
                products.append([line.product_id.id,line.product_uom_qty])
        self.order_id = self.order_line_id.order_id.id
        self.line_ids = [(0,0,{'product_id':product[0],'qty':product[1]}) for product in products]

    def create_requests(self):
        return

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def compute_invoice_status(self):
        self._compute_invoice_status()
        return True

    def get_to_invoice_qty(self):
        self._get_to_invoice_qty()
        return True

    def action_open_section_requisition(self):
        for order in self:
            action = self.env.ref('solibre_useability.action_sol_requisition').read()[0]
            return action

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False):
        for order in self:
            invoiceable_lines = order._get_invoiceable_lines(final)
            _logger.info(invoiceable_lines)
            if not invoiceable_lines:
                return order.invoice_ids.filtered(lambda i:i.state!=['draft','cancel'])
        return super(SaleOrder, self)._create_invoices(grouped, final)

    def _sms_get_number_fields(self):
        """ This method returns the fields to use to find the number to use to
        send an SMS on a record. """
        return ['mobile']

    def action_launch_stock_rule(self):
        for line in self.order_line:
            line._action_launch_stock_rule()
        return True

    def prepare_invoice(self):
        return self._prepare_invoice()

    def get_invoice_status(self):
        for sale in self:
            sale._get_invoice_status()
        return True

    @api.onchange('partner_id')
    def _set_warehouse(self):
        if self.partner_id.property_warehouse_id:
            self.warehouse_id = self.partner_id.property_warehouse_id.id

    def invoice_before_delivery(self):
        for order in self:
            order._force_lines_to_invoice_policy_order()
        moves = self._create_invoices()
        # if len(self) == 1:
        #     moves.action_post()
        return self.action_view_invoice()

    def create_requisition(self):
        return

    def send_order_confirmation_mail(self):
        return self._send_order_confirmation_mail()

    def share_sms(self):
        for sale in self:
            sale._message_sms_with_template(
                                template=self.env.ref('solibre_useability.sms_template_data_sale_order_share'),
                                partner_ids=sale.partner_id.ids,
                                put_in_queue=False
                            )

    @api.depends('invoice_ids', 'amount_total')
    def _get_amount_due(self):
        for sale in self:
            if not sale.invoice_ids:
                sale.amount_due = sale.amount_total
            else:
                sale.amount_due = sum(sale.invoice_ids.mapped('amount_residual'))

    @api.depends('amount_total')
    @api.onchange('order_line')
    def _get_available_limit(self):
        for order in self:
            order.available_credit = order.partner_id.credit_limit \
                                    - order.partner_id.credit \
                                    - order.amount_total
            order.credit_limit = order.partner_id.credit_limit

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({'payment_mode': self.payment_mode.id,
                    'partner_id_beneficiary': self.partner_id_beneficiary.id,
                    'beneficiary_delivery_date': self.beneficiary_delivery_date,
                    'company_id':self.company_id.id
                    })
        return res

    credit_limit = fields.Float(string="Credit Limit",compute='_get_available_limit',store=True)
    available_credit = fields.Float(string="Available Limit", compute='_get_available_limit',store=True)
    amount_due = fields.Float(string="Amount due", compute="_get_amount_due")
    approver_id = fields.Many2one(string="Approver", comodel_name="res.users") 
    weight = fields.Float(string="Weight", compute="get_weight")
    earliest_due_date = fields.Date(string="Worst Due Date", compute="get_payment_earliest_due_date")
    budget_id = fields.Many2one(string="Budget", comodel_name="crossovered.budget")
    requisition_count = fields.Integer(compute='_compute_mrp_count', string='RR count')
    subscription_count = fields.Integer(compute="compute_subscription", string='# subscriptions')
    delivery_instruction = fields.Text(string="Delivery instruction")
    payment_mode = fields.Many2one(string="Payment mode", comodel_name="account.journal",domain="[('type','=','bank')]")
    sale_url = fields.Char(string="Payment URL", compute="get_sale_url", store=True)
    partner_id_beneficiary = fields.Many2one(string="Beneficiary", comodel_name="res.partner")
    beneficiary_delivery_date = fields.Date(string="Benef. Delivery Date")
    pref_date = fields.Date(string="Delivery date")
    pickup_location_id = fields.Many2one(string="Pickup Location", comodel_name="res.company", copy=False)


    @api.model
    def create(self, vals):
        if not vals.get('analytic_account_id'):
            if vals.get('team_id') and not self.analytic_account_id:
                team = self.env['crm.team'].sudo().browse(vals.get('team_id'))
                if team:
                    vals.update({'analytic_account_id': team.analytic_account_id.id})
        return super(SaleOrder, self).create(vals)

    def write(self, vals):
        if not vals.get('analytic_account_id'):
            if vals.get('team_id'):
                team = self.env['crm.team'].sudo().browse(vals.get('team_id'))
                if team and not self.analytic_account_id:
                    vals.update({'analytic_account_id': team.analytic_account_id.id})
        # return super(SaleOrder, self).with_context(mail_auto_subscribe_no_notify=1).write(vals)
        return super(SaleOrder, self).write(vals)

    @api.depends('state')
    def get_sale_url(self):
        return True


    def compute_subscription(self):
        subscription_model = self.env['subscription.subscription']
        return subscription_model.compute_subscription(self)

    def action_view_subscription(self):
        subscription_model = self.env['subscription.subscription']
        context = {}
        context['default_name'] = self.name
        context['default_partner_id']  = self.partner_id.id
        return subscription_model.with_context(**context).action_view_subscription(self)

    def action_create_subscription(self, interval_number, interval_type, start_date, count):
        subscription_model = self.env['subscription.subscription']
        return subscription_model.action_create_subscription(self, interval_number, interval_type, start_date, count)


    def _compute_mrp_count(self):
        for order in self:
            # products = order.order_line.mapped('product_id.product_tmpl_id.id')
            # domain = [('product_tmpl_id', 'in', products)]
            # order.bom_count = self.env['mrp.bom'].search_count(domain)
            # domain = [('product_tmpl_id', 'in', products),('state','!=','approved')]
            # order.bom_pending_count = self.env['mrp.bom'].search_count(domain)
            # domain = [('origin', '=', order.name)]
            # order.mo_count = self.env['mrp.production'].search_count(domain)
            # order.sol_count = len(order.order_line.filtered(lambda l:l.product_id.type=='product'))
            if order.analytic_account_id:
                order.requisition_count = self.env['purchase.requisition'].search_count([('account_analytic_id', '=', order.analytic_account_id.id)])
            else:
                order.requisition_count = 0

    def action_open_requisition(self):
        for order in self:
            analytic_account_id = order.analytic_account_id.id
            return {
                'name': _('Resource requests'),
                'view_type': 'form',
                'view_mode': 'tree,form,kanban',
                'res_model': 'purchase.requisition',
                'domain': [('account_analytic_id', '=', analytic_account_id)],
                'context': {'default_account_analytic_id':analytic_account_id},
                'view_id': False,
                'type': 'ir.actions.act_window',
            }

    def create_project(self):
        if not self.origin:
            raise exceptions.ValidationError("Cannot create project withouf Project name")
        name = self.origin
        partner_id = self.partner_id.id
        if not self.analytic_account_id:
            project_id = self.env['project.project'].create({'name':name,
                                                             'allow_timesheets': True,
                                                             'company_id':self.env.user.company_id.id,
                                                             'privacy_visibility':'employees',
                                                             'partner_id':partner_id,})
            self.update({'analytic_account_id': project_id.analytic_account_id.id,
                        'project_id': project_id.id})

    def approval_request(self):
        approver = self.company_id.sale_approver_id
        if approver:
            note = "Request for approval %s" % self.name
            self.activity_schedule('solibre_useability.mail_act_sale_approval_request',
                                    note=note ,
                                    user_id=approver.id)
        return True


    @api.depends('partner_id')
    def get_payment_earliest_due_date(self):
        if self.partner_id:
            self.earliest_due_date = self.partner_id.payment_earliest_due_date
        else:
            self.earliest_due_date = False


    def get_weight(self):
        weight = 0
        for line in self.order_line:
            weight += line.product_id.weight * line.product_uom_qty
        self.weight = weight 


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        values={}
        values['credit_limit'] = self.partner_id.credit_limit
        values['available_credit'] = self.partner_id.credit_limit - self.partner_id.credit - self.amount_total
        if self.partner_id and self.partner_id.team_id:
            values['team_id'] = self.partner_id.team_id.id
        self.update(values)

    @api.onchange('payment_term_id')
    def onchange_payment_term(self):
        if not self.user_has_groups('sales_team.group_sale_manager'):
            DEFAULT_PAYMENT_TERM = 'account.account_payment_term_immediate'
            payment_term =  self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or self.env.ref(DEFAULT_PAYMENT_TERM, False).id 
            self.payment_term_id = payment_term


    def check_credit_limit(self):
        DEFAULT_PAYMENT_TERM = 'account.account_payment_term_immediate'
        payment_term =  self.env.ref(DEFAULT_PAYMENT_TERM, False).id
        allow = True
        reason = ''
        return allow, reason

    def create_budget(self):
        budget_obj = self.env['crossovered.budget']
        budget_line_obj = self.env['crossovered.budget.lines']
        budget_post_obj = self.env['account.budget.post']
        requisition_obj = self.env['purchase.requisition']
        requisition_line_obj = self.env['purchase.requisition.line']
        requisitions = []
        for order in self:
            if not order.budget_id:
                budget_id = budget_obj.search([('name', '=', order.analytic_account_id.name)])
                if not budget_id:
                    data = {'name':order.analytic_account_id.name,
                            'date_from':order.date_order,
                            'date_to':order.date_order}
                    budget_id = budget_obj.create(data)
                order.budget_id = budget_id.id
            else:
                budget_id = order.budget_id
            for line in order.order_line:
                if line.display_type and line.display_type=='line_section':
                    position_id = False
                    position_data = {'name': "Revenue for %s"%line.name}
                elif line.product_id:
                    if not position_id:
                        product_accounts = line.product_id.product_tmpl_id._get_product_accounts()
                        accounts = [product_accounts.get('income').id]
                        position_data.update({'account_ids': [(6, 0, accounts)]})
                        position_id = budget_post_obj.create(position_data)
                    budget_line_obj.create({'general_budget_id': position_id.id,
                                            'product_id': line.product_id.id,
                                            'crossovered_budget_id':budget_id.id,
                                            'analytic_account_id': order.analytic_account_id.id,
                                            'date_from': budget_id.date_from,
                                            'date_to': budget_id.date_to,
                                            'planned_amount': line.price_subtotal})



class SaleReport(models.Model):
    _inherit = 'sale.report'

    website_id = fields.Many2one('website', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['website_id'] = ", s.website_id as website_id"
        groupby += ', s.website_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
