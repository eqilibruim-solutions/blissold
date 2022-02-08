# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

import logging

_logger = logging.getLogger(__name__)

class SaleOrderSchedule(models.TransientModel):
    _name = 'sale.order.schedule'
    _description = 'Schedule delivery'

    schedule_type = fields.Selection(string="Schedule type", default="delivery",
                                     selection=[('delivery','Delivery'),
                                                ('pickup','Pick-Up'),])
    driver_id = fields.Many2one(string="Driver", comodel_name="res.partner")
    vehicle_id = fields.Many2one(string="Vehicle", comodel_name="fleet.vehicle")
    schedule_id = fields.Many2one(string="Existing Schedule", comodel_name="delivery.schedule",
                    domain=[('state', '!=', 'done')])

    @api.onchange('vehicle_id')
    def get_driver(self):
        if not self.vehicle_id.multiple_drivers:
            self.driver_id = self.vehicle_id.driver_id.id

    @api.onchange('driver_id')
    def get_vehicle(self):
        if self.driver_id and not self.vehicle_id.multiple_drivers:
            vehicle = self.env['fleet.vehicle'].search([('driver_id', '=', self.driver_id.id)],limit=1)
            if vehicle:
                self.vehicle_id = vehicle.id


    @api.onchange('schedule_type')
    def _change_schedule(self):
        vehicles = self.env['fleet.vehicle'].search([])
        drivers = vehicles.mapped('driver_id.id')
        domain = {'driver_id': [('id', 'in', drivers)]}
        return {'domain': domain}



    def create_schedule(self):
        active_ids =self.env.context.get('active_ids')
        model = self.env.context.get('active_model')
        orders = self.env[model].browse(active_ids)
        schedule_id = self.schedule_id
        if not schedule_id:
            data = {'vehicle_id': self.vehicle_id.id,
                    'driver_id': self.driver_id.id,
                    'schedule_type':self.schedule_type}
            schedule_id = self.env['delivery.schedule'].create(data)
        if self.schedule_type == 'delivery':
            orders.write({'schedule_id': schedule_id.id})
        else:
            orders.write({'pickup_schedule_id': schedule_id.id})
        orders.set_scheduled()
        # orders.create_cash_statement_lines(schedule_id)
        action = self.env.ref('solibre_sale_cod.action_delivery_schedule').read()[0]
        action['domain'] = [('id', 'in', schedule_id.ids)]
        return action  