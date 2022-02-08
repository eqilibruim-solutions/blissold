from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)

class UtmSource(models.Model):
    _inherit = 'utm.source'

    is_website = fields.Boolean(string="is website")

class UtmMedium(models.Model):
    # OLD crm.case.channel
    _inherit = 'utm.medium'

    is_website = fields.Boolean(string="is website")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sorting = fields.Char(string="Sorting", related="delivery_area_id.sorting")
    delivery_zone_id = fields.Many2one(string="Delivery Zone", comodel_name="delivery.zone")
    delivery_area_id = fields.Many2one(string="Delivery Area", comodel_name="delivery.area")


class SaleReport(models.Model):
    _inherit = 'sale.report'

    delivery_zone_id = fields.Many2one(string="Delivery Zone", comodel_name="delivery.zone")
    delivery_area_id = fields.Many2one(string="Delivery Area", comodel_name="delivery.area")


    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['delivery_zone_id'] = ", s.delivery_zone_id as delivery_zone_id"
        fields['delivery_area_id'] = ", s.delivery_area_id as delivery_area_id"

        groupby += ', s.delivery_zone_id, s.delivery_area_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)