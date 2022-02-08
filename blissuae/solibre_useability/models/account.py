from odoo import models, fields, api, exceptions, _
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    vehicle_id = fields.Many2one(string="Fleet", comodel_name="fleet.vehicle")
    user_id = fields.Many2one(string="Employee", comodel_name="res.users", related="vehicle_id.user_id")

    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        if self.vehicle_id:
            self.user_id = self.vehicle_id.user_id.id
            self.analytic_account_id = self.vehicle_id.analytic_account_id.id

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    iban = fields.Char(string="Iban")
    branch = fields.Char(string="Branch")

class AccountAccountType(models.Model):
    _inherit = 'account.account.type'

    _order = 'sequence'

    sequence = fields.Integer(default=10)

class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_in_words = fields.Char(string="Amount in Words", compute="get_amount_in_words")
    landing_cost_main_id = fields.Many2one(string="Landing Cost Main", comodel_name="account.landing.cost")
    landing_cost_add_id = fields.Many2one(string="Landing Cost Additional", comodel_name="account.landing.cost")
    prepayment_invoice_id = fields.Many2one(string="Prepayment invoice", comodel_name="account.move")
    prepayment_frequency = fields.Selection([('no', 'No'),
                                             ('daily', 'Daily'),
                                             ('weekly', 'Weekly'),
                                             ('monthly', 'Monthly'),
                                             ('yearly', 'Yearly')],
                                             'Amortisation Frequency', default='no',required=True)
    prepayment_move_ids = fields.One2many(string="Prepayment moves", comodel_name="account.move", inverse_name="prepayment_invoice_id")
    prepayment_amount = fields.Float(string="Amortisation amount")
    prepayment_start_date = fields.Date(string="Start date")
    prepayment_account_id = fields.Many2one(string="Expense account", comodel_name="account.account")
    prepayment_balance = fields.Float(string="Balance", compute="get_prepayment_balance")
    prepayment_allocated = fields.Float(string="Balance", compute="get_prepayment_balance")
    subscription_count = fields.Integer(compute="compute_subscription", string='# subscriptions')
    payment_mode = fields.Many2one(string="Payment mode", comodel_name="account.journal",domain="[('type','=','bank')]")
    payment_url = fields.Char(string="Payment URL", compute="get_payment_url")
    partner_id_beneficiary = fields.Many2one(string="Beneficiary", comodel_name="res.partner")
    beneficiary_delivery_date = fields.Date(string="Benef. Delivery Date")
    amount_discount = fields.Monetary(string="Discount", compute="get_total_discount")
    print_company_id = fields.Many2one(string="Print company", comodel_name="res.company")

    def get_total_discount(self):
        for inv in self:
            inv.amount_discount = sum(inv.invoice_line_ids.mapped('line_discount'))

    def get_payment_url(self):
        for invoice in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            acq = self.env['payment.acquirer'].search([('state', '=', 'enabled')])
            url = False
            if not invoice.access_token:
                invoice._get_share_url()
            if invoice.amount_residual>0 and acq:
                url= '%s%s%s'%(base_url, '/pay/account.move/', invoice.access_token)
            invoice.payment_url = url 

    def compute_subscription(self):
        subscription_model = self.env['subscription.subscription']
        return subscription_model.compute_subscription(self)

    def action_view_subscription(self):
        subscription_model = self.env['subscription.subscription']
        context = {}
        context['default_name'] = "Recurring %s" % self.name
        context['default_partner_id']  = self.partner_id.id
        return subscription_model.with_context(**context).action_view_subscription(self)


    def action_create_subscription(self, interval_number, interval_type, start_date, count):
        subscription_model = self.env['subscription.subscription']
        return subscription_model.action_view_subscription(self, interval_number, interval_type, start_date, count)


    def scheduler_amortise_prepayment(self):
        # This method is called by a cron task
        # It creates costs for contracts having the "recurring cost" field setted, depending on their frequency
        # For example, if a contract has a reccuring cost of 200 with a weekly frequency, this method creates a cost of 200 on the
        # first day of each week, from the date of the last recurring costs in the database to today
        # If the contract has not yet any recurring costs in the database, the method generates the recurring costs from the start_date to today
        # The created costs are associated to a contract thanks to the many2one field contract_id
        # If the contract has no start_date, no cost will be created, even if the contract has recurring costs
        AccountMove = self.env['account.move']
        AML = self.env['account.move.line']

        deltas = {
            'yearly': relativedelta(years=+1),
            'monthly': relativedelta(months=+1),
            'weekly': relativedelta(weeks=+1),
            'daily': relativedelta(days=+1)
        }
        if self:
            invoices = self.filtered(lambda i:i.prepayment_frequency!='no')
        else:
            invoices = self.env['account.move'].search([('prepayment_frequency', '!=', 'no')], offset=0, limit=None, order=None)
        for invoice in invoices:
            if invoice.prepayment_balance <= 0 :
                invoice.prepayment_frequency = 'no'
                continue
            found = False
            startdate = invoice.prepayment_start_date
            if invoice.prepayment_move_ids:
                last_autogenerated_cost = AccountMove.search([
                    ('prepayment_invoice_id', '=', invoice.id),
                ], offset=0, limit=1, order='date desc')
                if last_autogenerated_cost:
                    found = True
                    startdate = last_autogenerated_cost.date
            if found:
                startdate += deltas.get(invoice.prepayment_frequency)
            today = fields.Date.context_today(self)
            while (startdate <= today and invoice.prepayment_balance>0):
                ratio = min(invoice.prepayment_balance, invoice.prepayment_amount) / invoice.amount_untaxed
                imls = invoice.invoice_line_ids
                lines = []
                for iml in imls:
                    std_lines = iml.copy_data()
                    rev_lines = iml.copy_data()

                    std_lines = [(0, 0, l) for l in std_lines]
                    rev_lines = [(0, 0, l) for l in rev_lines]

                    for line in std_lines:
                        debit = line[2]['debit'] * ratio
                        credit = line[2]['credit'] * ratio
                        line[2]['debit'] = credit
                        line[2]['credit'] = debit
                        line[2].pop('tax_ids')
                        line[2].pop('move_id')
                        line[2].pop('tag_ids')

                    for line in rev_lines:
                        debit = line[2]['debit'] * ratio
                        credit = line[2]['credit'] * ratio
                        line[2]['account_id'] = invoice.prepayment_account_id.id
                        line[2]['debit'] = debit
                        line[2]['credit'] = credit
                        line[2].pop('tax_ids')
                        line[2].pop('move_id')
                        line[2].pop('tag_ids')

                    lines += std_lines
                    lines += rev_lines
                    

                _logger.info(lines)
                data = {
                    'type': 'entry',
                    'company_id': invoice.company_id.id,
                    'partner_id': invoice.partner_id.id,
                    'date': startdate,
                    'prepayment_invoice_id': invoice.id,
                    'ref': "Prepayment Amort. %s" % invoice.name,
                    'line_ids': lines,
                    'journal_id':self.env['account.journal'].search([('code','=','MISC'),('company_id','=',invoice.company_id.id)]).id
                }
                _logger.info(lines)
                move = AccountMove.create(data)
                move.post()
                startdate += deltas.get(invoice.prepayment_frequency)
        return True

    @api.depends('prepayment_move_ids')
    def get_prepayment_balance(self):
        AML = self.env['account.move.line']

        for invoice in self:
            move_lines = AML.search([('move_id', 'in', invoice.prepayment_move_ids.ids),('move_id.state','not in',['cancel','draft'])])
            prepayment_allocated = sum(move_lines.filtered(lambda m: m.credit > 0).mapped('credit'))
            prepayment_balance = invoice.amount_untaxed - prepayment_allocated
            invoice.update({'prepayment_allocated': prepayment_allocated,
                            'prepayment_balance': prepayment_balance})


    def run_scheduler(self):
        self.scheduler_amortise_prepayment()
        
    @api.depends('amount_total')
    def get_amount_in_words(self):
        self.amount_in_words = self.currency_id.amount_to_text(self.amount_total)

    def recompute_tax_lines(self):
        self = self.with_context(check_move_validity=False)
        self._recompute_tax_lines()
        return True

    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        return True

    def onchange_partner_id(self):
        self = self.with_context(check_move_validity=False)        
        self._onchange_partner_id()
        return True

    def post(self):
        res = super(AccountMove, self).post()
        return True
        
    def action_invoice_print(self):
        if self.invoice_payment_term_id.block_unpaid and self.amount_residual > 0:
            raise exceptions.ValidationError("Cannot print unpaid invoices")
        return super(AccountMove, self).action_invoice_print()


    # def write(self, vals):
    #     _logger.info(vals)
    #     return super(AccountMove, self).write(vals)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _order = "user_type_id, date desc, move_name desc, id"


    line_discount = fields.Monetary(string="Line discount", comodel_name="account.invoice", compute="get_discount")
    line_taxable = fields.Monetary(string="taxable", comodel_name="account.invoice", compute="get_discount")
    line_tax = fields.Monetary(string="Line discount", comodel_name="account.invoice", compute="get_discount")
    user_type_id = fields.Many2one('account.account.type', 
                                            related='account_id.user_type_id',
                                            string="Account Type", store=True, readonly=True)

    def get_discount(self):
        for line in self:
            line.line_discount = line.price_unit - (line.price_unit * (1 - (line.discount / 100.0)))
            line.line_tax = line.price_total - line.price_subtotal
            line.line_taxable = line.price_unit - line.line_discount

    def onchange_product_id(self):
        self = self.with_context(check_move_validity=False)
        _logger.info(self.env.user.name)
        self._onchange_product_id()
        self._onchange_mark_recompute_taxes()
        self._onchange_price_subtotal()
        return True

    @api.model
    def load(self, fields, data):
        """ Overridden for better performances when importing a list of account
        with opening debit/credit. In that case, the auto-balance is postpone
        until the whole file has been imported.
        """
        self = self.with_context(check_move_validity=False)
        rslt = super(AccountMoveLine, self).load(fields, data)
        return rslt

    # def write(self, vals):
    #     _logger.info(vals)
    #     return super(AccountMoveLine, self).write(vals)

class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    block_unpaid =  fields.Boolean(string="Block unpaid")

class payment_register(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Register Payment'

    communication = fields.Char(string="Memo")
    
    def _prepare_payment_vals(self, invoices):
        vals = super(payment_register,self)._prepare_payment_vals(invoices)
        if self.communication:
            vals.update({'communication':self.communication})
        return vals
