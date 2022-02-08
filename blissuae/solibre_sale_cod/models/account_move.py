from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    reinvoice_ids = fields.Many2many('account.move', 'account_move_reinvoice_rel', 'origin_move_id', 'reinvoice_move_id', string='Re-invoiced')

    def _franchise_create_invoices(self):
        return

    def _franchise_prepare_invoice_data(self,partner_id):
        self.ensure_one()
        return {

        }


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _franchise_prepare_invoice_line_data(self):
        ''' Get values to create the invoice line.
        :param company: The targeted company.
        :return: Python dictionary of values.
        '''
        self.ensure_one()

        return {

        }
    