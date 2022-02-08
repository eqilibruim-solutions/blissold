from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)


class ProcurementRule(models.Model):

    _inherit = 'stock.rule'

    def _get_matching_bom(self, product_id, company_id, values):
        res = super(ProcurementRule, self)._get_matching_bom(product_id, company_id, values)
        if not res:
            data = {
                'product_tmpl_id': product_id.product_tmpl_id.id,
                'product_id': product_id.id,
                'type': 'normal',
                'code': 'Auto',
                'product_uom_id': product_id.uom_id.id,}
            bom_copy = self.env['mrp.bom'].search([('code', '=', 'Template')],limit=1)
            if bom_copy:
                res = bom_copy.copy(data)
            else:
                res = self.env['mrp.bom'].create(data)
        return res

    