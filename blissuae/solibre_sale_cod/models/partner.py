from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_duplicate = fields.Boolean(string="Duplicate")

    def get_duplicates(self):
        duplicates = self.env['res.partner'].search([('email', '=', self.email), ('parent_id', '=', False)])
        if len(duplicates)>1:
            return duplicates.ids
        return []

    def get_is_duplicate(self):
        self.ensure_one()
        if not self.parent_id and not self.email:
            return False
        if self.is_duplicate:
            return True
        duplicates = self.env['res.partner'].search([('email', '=', self.email), ('parent_id', '=', False)])
        if len(duplicates)>1:
            duplicates.write({'is_duplicate':True})
            return True
        else:
            return False

    def merge_duplicates(self):
        duplicates = self.get_duplicates()
        if len(duplicates) > 1:
            _logger.info("Merging %s"%duplicates)
            wizard = self.env['base.partner.merge.automatic.wizard']
            merge = wizard.create({'partner_ids': [(6,0,duplicates)], 'dst_partner_id': duplicates[0],})
            merge.action_merge()
        return False

    def auto_signup(self):
        for partner in self:
            if not partner.get_is_duplicate() and not partner.user_ids:
                wizard = self.env['portal.wizard']
                portal = wizard.create({'user_ids': [(0,0,{'partner_id':partner.id,'email':partner.email,'in_portal':True})]})
                portal.action_apply()
        return True