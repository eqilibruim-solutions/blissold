from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    _order = 'pref_date'

    pref_date = fields.Date(string="Delivery date", related="sale_id.pref_date", store=True)
    sale_id = fields.Many2one(string="Sale Order", comodel_name="sale.order", compute="get_sale_order")

    @api.depends('production_id')
    def get_sale_order(self):
        for wo in self:
            sale_id = False
            if wo.production_id and wo.production_id.origin:
                sale = self.env['sale.order'].sudo().search([('name', '=', wo.production_id.origin)], limit=1)
                if sale:
                    sale_id = sale.id
            wo.sale_id = sale_id

    def button_start(self):
        self.ensure_one()
        if self.sale_id:
            self.sale_id.sudo().picking_ids.set_accepted()
            self.action_set_picking_state()
        res = super(MrpWorkorder, self).button_start()
        return res


    def action_set_picking_state(self):
        if self.sale_id:
            self.sale_id.sudo().picking_ids.write({'workorder_status':'%s'%self.state})            


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def set_confirmation(self):
        return True