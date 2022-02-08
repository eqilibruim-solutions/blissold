from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    user_id = fields.Many2one(string="Employee", comodel_name="res.users",domain="[('share','=',False)]")
    analytic_account_id = fields.Many2one(string="Analytic Account", comodel_name="account.analytic.account")

    @api.onchange('user_id')
    def onchange_employee(self):
        if self.user_id:
            self.driver_id = self.user_id.partner_id.id

    def _compute_count_all(self):
        Odometer = self.env['fleet.vehicle.odometer']
        LogFuel = self.env['fleet.vehicle.log.fuel']
        LogService = self.env['fleet.vehicle.log.services']
        LogContract = self.env['fleet.vehicle.log.contract']
        Cost = self.env['account.analytic.line']
        for record in self:
            record.odometer_count = Odometer.search_count([('vehicle_id', '=', record.id)])
            record.fuel_logs_count = LogFuel.search_count([('vehicle_id', '=', record.id)])
            record.service_count = LogService.search_count([('vehicle_id', '=', record.id)])
            record.contract_count = LogContract.search_count([('vehicle_id', '=', record.id),('state','!=','closed')])
            record.cost_count = Cost.search_count([('account_id', '=', record.analytic_account_id.id)])
            record.history_count = self.env['fleet.vehicle.assignation.log'].search_count([('vehicle_id', '=', record.id)])

    def act_show_log_cost(self):
        """ This opens log view to view and add new log for this vehicle, groupby default to only show effective costs
            @return: the costs log view
        """
        return


    def create_analytic(self):
        for veh in self:
            if not veh.analytic_account_id:
                veh.analytic_account_id = self.env['account.analytic.account'].create({
                                          'code':veh.license_plate,
                                          'name':veh.model_id.name}).id 
        return True      

    @api.model
    def create(self, vals):
        res = super(FleetVehicle,self).create(vals)
        res.create_analytic()
        return res