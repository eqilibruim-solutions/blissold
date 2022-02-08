from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    validation_user_id = fields.Many2one(string="Validated by", comodel_name="res.users")
    sale_user_id = fields.Many2one(string="Sale user", comodel_name="res.users", related="sale_id.user_id", store=True)



class StockMove(models.Model):
    _inherit = 'stock.move'

    mrp_available_stock = fields.Float(string="Available Stock", compute="get_mrp_available_stock", store=True)

    def get_mrp_available_stock(self):
        for line in self:
            if line.production_id:
                line.mrp_available_stock = line.product_id.with_context(warehouse=line.location_id.get_warehouse().id).qty_available
            else:
                line.mrp_available_stock = 0

    def create_account_move(self, cancel_backorder=False):
        # Init a dict that will group the moves by valuation type, according to `move._is_valued_type`.
        valued_moves = {valued_type: self.env['stock.move'] for valued_type in self._get_valued_types()}
        for move in self:
            for valued_type in self._get_valued_types():
                if getattr(move, '_is_%s' % valued_type)():
                    valued_moves[valued_type] |= move
                    continue

        # AVCO application
        valued_moves['in'].product_price_update_before_done()


        # '_action_done' might have created an extra move to be valued
        for move in self:
            for valued_type in self._get_valued_types():
                if getattr(move, '_is_%s' % valued_type)():
                    valued_moves[valued_type] |= move
                    continue

        stock_valuation_layers = self.env['stock.valuation.layer'].sudo()
        # Create the valuation layers in batch by calling `moves._create_valued_type_svl`.
        for valued_type in self._get_valued_types():
            todo_valued_moves = valued_moves[valued_type]
            if todo_valued_moves:
                todo_valued_moves._sanity_check_for_valuation()
                stock_valuation_layers |= getattr(todo_valued_moves, '_create_%s_svl' % valued_type)()
                continue


        for svl in stock_valuation_layers:
            if not svl.product_id.valuation == 'real_time':
                continue
            if svl.currency_id.is_zero(svl.value):
                continue
            svl.stock_move_id.with_context(force_period_date=svl.stock_move_id.date)._account_entry_move(svl.quantity, svl.description, svl.id, svl.value)

        stock_valuation_layers._check_company()

        # For every in move, run the vacuum for the linked product.
        products_to_vacuum = valued_moves['in'].mapped('product_id')
        company = valued_moves['in'].mapped('company_id') and valued_moves['in'].mapped('company_id')[0] or self.env.company
        for product_to_vacuum in products_to_vacuum:
            product_to_vacuum._run_fifo_vacuum(company)

        return True