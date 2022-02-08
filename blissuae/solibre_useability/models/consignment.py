from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)


class ConsignmentSale(models.Model):
    _name = 'consignment.sale'
    _description = 'Consignment Sale'

    name = fields.Char(string="Reference")
    date = fields.Date(string="Date", default=fields.Date.context_today)
    user_id = fields.Many2one(string="User", comodel_name="res.users", default=lambda self:self.env.user)
    consignee_partner_id = fields.Many2one(string="Consignee", comodel_name="res.partner")
    partner_id = fields.Many2one(string="Customer", comodel_name="res.partner")
    product_id = fields.Many2one(string="Product", comodel_name="product.product")
    quantity = fields.Float(string="Quantity")
    product_uom_category_id = fields.Many2one(comodel_name='uom.category',related='product_id.uom_id.category_id', readonly=True)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    move_id = fields.Many2one(string="Consignement", 
                              comodel_name="stock.move", 
                              domain="[('partner_id','=',consignee_partner_id),('product_id','=',product_id),('state','not in',('done','cancel'))]")
    state = fields.Selection(string="State", default='draft',selection=[('draft','Draft'),('done','Done')])

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.ensure_one()
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id


    def unlink(self):
        for order in self:
            if order.state not in ('draft', 'cancel'):
                raise UserError(_('You can not delete a sent quotation or a confirmed sales order. You must first cancel it.'))
        return super(ConsignmentSale, self).unlink()


