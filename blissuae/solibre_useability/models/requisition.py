from odoo import models, fields, api, exceptions, _
from odoo.addons.purchase_requisition.models.purchase_requisition import PURCHASE_REQUISITION_STATES
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.tools import float_compare, float_is_zero

# PURCHASE_REQUISITION_STATES.pop(PURCHASE_REQUISITION_STATES.index(('open', 'Bid Selection')))
PURCHASE_REQUISITION_STATES.append(('open', 'Approved'))


class PurchaseRequisitionType(models.Model):

    _inherit = 'purchase.requisition.type'

    picking_type_id = fields.Many2one(string="Transfer type", comodel_name="stock.picking.type", help="Only for internal moves")
    auto_approve = fields.Boolean(string="Auto approve PO")
    block_price = fields.Boolean(string="Prevent price change")
    categ_ids = fields.One2many(string="Categories", comodel_name="product.category", inverse_name="requisition_type_id")
    user_id = fields.Many2one(string="Responsible", comodel_name="res.users")
    company_id = fields.Many2one(string="Company", comodel_name="res.company")

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    payment_id = fields.Many2one(string="Payment", comodel_name="account.payment")
    procurement_pref = fields.Selection(string="Preference", 
                                        default='none',
                                        required=True,
                                        selection=[('local', 'Local'), ('import', 'Import'), ('none', 'None')])
    manager_user_id = fields.Many2one(string="Approved by", comodel_name="res.users")
    total_amount = fields.Monetary(string="Total Cost", compute="get_total")
    picking_id = fields.Many2one(string="Picking", comodel_name="stock.picking")
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    transfer_type_id = fields.Many2one(string="Transfer type", comodel_name="stock.picking.type", related="type_id.picking_type_id")
    total_amount = fields.Monetary(string="Total Cost", compute="get_total")
    total_estimate = fields.Monetary(string="Total Estimated", compute="get_total")
    line_ids = fields.One2many('purchase.requisition.line', 'requisition_id', string='Products to Purchase', states={'draft': [('readonly', False)]}, copy=True, readonly=True)
    purchaser_user_id = fields.Many2one(string="Purchaser", comodel_name="res.users", related="type_id.user_id", store=True)
    categ_id = fields.Many2one(string="Category", comodel_name="product.category")
    pref_supplier_id = fields.Many2one(string="Preffered supplier", comodel_name="res.partner")
    order_state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Order', readonly=True, copy=False, default=False)

    @api.onchange('categ_id')
    def _onchange_categ_id(self):
        if self.categ_id:
            categ_ids = [self.categ_id.id]
            all_categ = self.env.ref('product.product_category_all')
            if all_categ:
                categ_ids.append(all_categ.id)
            return {'domain': {'line_ids.product_id': [('category_id', 'in', categ_ids)]}}

    def reload_unit_price(self):
        for req in self:
            for line in req.line_ids:
                line.price_unit = line.get_price()

    @api.onchange('line_ids')
    def get_total(self):
        for req in self:
            req.total_amount = sum(req.line_ids.mapped('price_subtotal'))
            req.total_estimate = sum(req.line_ids.mapped('estimated_cost'))


    def action_in_progress(self):
        res = super(PurchaseRequisition, self).action_in_progress()
        approver = self.sudo().user_id.employee_ids and self.sudo().user_id.employee_ids[0].parent_id.user_id or False
        if approver:
            note = "Request for approval %s %s" % (self.name,
                                                   self.account_analytic_id and self.account_analytic_id.name or '')
            self.activity_schedule('solibre_useability.mail_act_requisition_approval_request',
                                note=note,
                                user_id=approver.id)
        return res


    @api.onchange('type_id')
    def change_picking_type(self):
        self.transfer_type_id = self.type_id.picking_type_id.id

    def create_and_confirm_po(self):
        if self.pref_supplier_id:
            prices = [price > 0 for price in self.line_ids.mapped('price_unit')]
            to_delete = self.line_ids.filtered(lambda l:l.product_qty == 0)
            to_delete.unlink()
            if all(prices):
                PurchaseOrder = self.env['purchase.order']
                po_data = {'partner_id': self.pref_supplier_id.id, 'requisition_id': self.id}
                if self.account_analytic_id:
                    po_data.update({'analytic_account_id': self.account_analytic_id.id})
                purchase_order = PurchaseOrder.new(po_data)
                purchase_order._onchange_requisition_id()
                for line in purchase_order.order_line.filtered(lambda l:l.product_id.type == 'service'):
                    line.account_analytic_id = self.account_analytic_id.id
                po_dict = purchase_order._convert_to_write({name: purchase_order[name] for name in purchase_order._cache})
                purchase_order = PurchaseOrder.create(po_dict)
                purchase_order.button_confirm()
            else:
                message = "Unable to process purchase order, prices missing"
                self.activity_schedule('mail.mail_activity_data_warning', note=message, user_id=self.user_id.id)


    def action_draft(self):
        self.ensure_one()
        # self.name = 'New'
        self.write({'state': 'draft'})

    def action_open(self):
        if self.name == 'New':
            if self.is_quantity_copy != 'none':
                self.name = self.env['ir.sequence'].next_by_code('purchase.requisition.purchase.tender')
            else:
                self.name = self.env['ir.sequence'].next_by_code('purchase.requisition.blanket.order')
        if self.env.user.employee_ids:
            if self.env.user.id == self.sudo().user_id.employee_ids[0].parent_id.user_id.id or \
            self.user_has_groups('purchase.group_purchase_manager') or \
            self.type_id.auto_approve:
                self.write({'manager_user_id': self.env.user.id})
                self.activity_feedback(['solibre_useability.mail_act_requisition_approval_request'])
                self.create_and_confirm_po()
                self.consume_move()
                res = super(PurchaseRequisition, self).action_open()
                return res
            else:
                raise exceptions.UserError("Only a purchase manager or hierarchical manager can approve !")
        else:
            raise exceptions.UserError("Approver has to be an employee!")


    def consume_move(self):
        for req in self:
            req._create_picking()
        return True

    @api.model
    def _prepare_picking(self):
        location_id = self.type_id.picking_type_id.default_location_src_id.id
        location_destination_id = self.user_id.partner_id.property_stock_customer.id

        return {
            'picking_type_id': self.type_id.picking_type_id.id,
            'partner_id': self.user_id.partner_id.id,
            'validation_user_id': self.env.user.id,
            'origin': self.name,
            'location_dest_id': location_destination_id,
            'location_id': location_id
        }

    def _create_picking(self):
        pickings = []
        for order in self:
            if order.type_id.picking_type_id and not order.picking_id:
                warehouses = []

                if any([ptype in ['product', 'consu'] for ptype in order.line_ids.mapped('product_id.type')]):
                    res = order._prepare_picking()
                    picking = self.env['stock.picking'].create(res)
                    order.picking_id = picking.id
                    order.line_ids.filtered(lambda r: r.product_id.type in ['product', 'consu'])._create_stock_moves(picking)
                    pickings.append(picking.id)
        if pickings:
            pickings = self.env['stock.picking'].search([('id','in',pickings)])
            for picking in pickings:
                try:
                    picking.action_assign()
                except:
                    continue

        return True

class PurchaseRequisitionLine(models.Model):

    _inherit = 'purchase.requisition.line'


    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            location_id = picking.location_id
            location_destination_id = picking.location_dest_id
            template = {
                'name': line.product_id.name or '',
                'product_id': line.product_id.id,
                'product_uom': line.product_uom_id.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'picking_id': picking.id,
                'partner_id': picking.partner_id.id,
                'state': 'draft',
                'company_id': line.requisition_id.company_id.id,
                'picking_type_id': picking.picking_type_id.id,
                'origin': line.requisition_id and line.requisition_id.name,
                'route_ids': picking.picking_type_id.warehouse_id and [(6, 0, [x.id for x in picking.picking_type_id.warehouse_id.route_ids])] or [],
                'warehouse_id': picking.picking_type_id.warehouse_id.id,
            }




            # Fullfill all related procurements with this po line
            diff_quantity = line.product_qty

            if float_compare(diff_quantity, 0.0, precision_rounding=line.product_uom_id.rounding) > 0:
                template['product_uom_qty'] = diff_quantity
                done += moves.create(template)
        return done


    @api.onchange('product_id')
    @api.depends('product_id')
    def _get_available_qty(self):
        for line in self:
            line.available_qty = line.product_id.qty_available
            line.forecast_qty = line.product_id.incoming_qty

    def _prepare_purchase_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        self.ensure_one()
        name = self.name
        res = super(PurchaseRequisitionLine, self)._prepare_purchase_order_line(name, product_qty, price_unit, taxes_ids)
        res['employee_id'] = self.employee_id
        return res

    @api.onchange('product_qty', 'price_unit')
    def _change_quantity(self):
        for line in self:
            domain = {'product_uom_id': [('category_id', '=', line.product_id.uom_id.category_id.id)]}
            if line.requisition_id.type_id.categ_ids:
                domain['product_id'] = [('category_id','in',line.requisition_id.type_id.categ_ids.ids)]
            if not line.product_id:
                return {'domain': domain}
            price_unit = line.get_price()
            data = {'price_unit': price_unit,
                    'price_subtotal': price_unit * line.product_qty}
            line.update(data)
        return {'domain': domain}

    available_qty = fields.Float(string="On Hand", compute="_get_available_qty")
    forecast_qty = fields.Float(string="Incoming", compute="_get_available_qty")
    price_unit = fields.Float(string='Prev. Unit Price', digits='Product Price')
    price_subtotal = fields.Float(string='Subtotal')
    estimated_cost = fields.Float(string="Budget/Estimate")
    employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee")
    name = fields.Char(string="Description")


    def _get_product_purchase_description(self, product_lang):
        self.ensure_one()
        name = product_lang.display_name
        if product_lang.description_purchase:
            name += '\n' + product_lang.description_purchase

        return name

    @api.onchange('product_id')
    def get_line_name(self):
        if not self.product_id:
            return
        product_lang = self.product_id.with_context(
            lang=self.env.user.partner_id.lang,
            partner_id=self.env.user.partner_id.id,
            company_id=self.env.company.id,
        )
        self.name = self._get_product_purchase_description(product_lang)

    def get_price(self):
        self.ensure_one()
        if self.product_id:
            line = self
            params = {'order_id': line}
            seller = line.product_id._select_seller(
                partner_id=line.requisition_id.pref_supplier_id,
                quantity=line.product_qty,
                date=datetime.now().date(),
                uom_id=line.product_uom_id,
                params=params)
            if not seller:
                return self.product_id.standard_price
            else:
                price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price, line.product_id.supplier_taxes_id, line.product_id.supplier_taxes_id, line.company_id) if seller else 0.0
                if price_unit and seller and line.requisition_id.currency_id and seller.currency_id != line.requisition_id.currency_id:
                    price_unit = seller.currency_id._convert(
                        price_unit, line.requisition_id.currency_id, line.requisition_id.company_id, fields.Date.today())

                if seller and line.product_uom_id and seller.product_uom != line.product_uom_id:
                    price_unit = seller.product_uom._compute_price(price_unit, line.product_uom_id)
                if price_unit == 0:
                    price_unit = line.product_id.standard_price
                return price_unit

    @api.onchange('price_unit')
    def change_price(self):
        for line in self:
            if line.requisition_id.type_id.block_price:
                price_unit = line.get_price()
                if price_unit != line.price_unit:
                    line.price_unit = price_unit


    def create_po(self):
        if self.requisition_id.state not in ['open']:
            raise exceptions.ValidationError("Approval required")
        PurchaseOrder = self.env['purchase.order']
        po_data = {'partner_id': self.company_id.partner_id.id, 
                   'requisition_id': self.requisition_id.id,
                   'requisition_line_id': self.id}
        if self.requisition_id.account_analytic_id:
            po_data.update({'analytic_account_id': self.requisition_id.account_analytic_id.id})
        purchase_order = PurchaseOrder.new(po_data)
        purchase_order._onchange_requisition_id()
        po_dict = purchase_order._convert_to_write({name: purchase_order[name] for name in purchase_order._cache})
        purchase_order = PurchaseOrder.create(po_dict)
        for line in purchase_order.order_line.filtered(lambda l:l.product_id != self.product_id):
            line.unlink()
        [action] = self.env.ref('purchase.purchase_rfq').read()
        action['domain'] = [('id', '=', purchase_order.id)]

        return action
