from odoo import models, fields, api, exceptions, _
import requests
import logging
import json
_logger = logging.getLogger(__name__)
    

class SaleOrderTrackingActivity(models.Model):
    _name = 'sale.order.tracking.activity'
    _description = 'Sale Order Tracking Activity'

    name = fields.Char(string="Name")

class SaleOrderTrackingActivityState(models.Model):
    _name = 'sale.order.tracking.activity.state'
    _description = 'Sale Order Tracking Activity State'
    _order = 'sequence'
    sequence = fields.Integer(required=True, default=1)
    activity_id = fields.Many2one(string="Activity", comodel_name="sale.order.tracking.activity")
    name = fields.Char(string="State")
    published = fields.Boolean(string="Published")
    icon = fields.Char(string="icon")

class SaleOrderTracking(models.Model):
    _name = 'sale.order.tracking'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'order_id'
    _order = 'create_date desc'
    _description = 'Order Tracking'

    activity_id = fields.Many2one(string="Activity", comodel_name="sale.order.tracking.activity")
    state_id = fields.Many2one(string="State",comodel_name="sale.order.tracking.activity.state")
    order_id = fields.Many2one(string="Order", comodel_name="sale.order")
    department_id = fields.Many2one(string="Department", comodel_name="hr.department", compute="get_department")
    note = fields.Char(string="Comments")

    def update_franchise(self, vals):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        franchise_url = ICPSudo.get_param('franchise_url')
        if franchise_url == "False":
            franchise_url = False
        if franchise_url:
            values = vals
            values['activity_id'] = self.env['sale.order.tracking.activity'].browse(vals.get('activity_id')).get_external_id()[vals.get('activity_id')]
            values['state_id'] = self.env['sale.order.tracking.activity.state'].browse(vals.get('state_id')).get_external_id()[vals.get('state_id')]
            values['order_id'] = self.env['sale.order'].browse(vals.get('order_id')).name
            url = '%s/new_sale_tracking'%(franchise_url)
            result = requests.post(url,values)

    @api.model
    def create(self, vals):
        res = super(SaleOrderTracking, self).create(vals)
        self.update_franchise(vals)
        return res

    # @api.model
    # def create(self, vals):
    #     order = self.env['sale.order'].browse(vals.get('order_id'))
    #     if order.shipping_state == 'delivered':
    #         raise exceptions.ValidationError("Shipment already delivered")
    #     return super(SaleOrderTracking, self).write(vals)

    def get_department(self):
        for tracking in self:
            employee = self.env['hr.employee'].search([('user_id','=',tracking.create_uid.id)])
            if employee:
                tracking.department_id = employee.department_id.id
            else:
                tracking.department_id = False
