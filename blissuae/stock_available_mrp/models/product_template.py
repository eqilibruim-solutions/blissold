# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api

import logging

_logger = logging.getLogger(__name__)
    
class ProductTemplate(models.Model):
    _inherit = 'product.template'


    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        combination_info = super(ProductTemplate, self)._get_combination_info(combination, product_id, add_qty, pricelist, parent_combination, only_template)
        if combination_info['product_id']:
            product = self.env['product.product'].sudo().browse(combination_info['product_id'])
            combination_info.update({
                'bom_ids': product.bom_ids,
                'immediately_usable_qty': product.immediately_usable_qty
            })
        else:
            product_template = self.sudo()
            combination_info.update({
                'bom_ids': product_template.bom_ids,
                'immediately_usable_qty': product_template.immediately_usable_qty
            })
        return combination_info
