from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)
    
class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    code = fields.Char(
        string='Project Number', default="/", readonly=True)

    _sql_constraints = [
        ('project_task_unique_code', 'UNIQUE (code)',
         _('The code must be unique!')),
    ]

    @api.model
    def create(self, vals):
        if vals.get('code', '/') == '/':
            vals['code'] = self.env['ir.sequence'].next_by_code('project.project')
        return super(AnalyticAccount, self).create(vals)

    def copy(self, default=None):
        if default is None:
            default = {}
        default['code'] = self.env['ir.sequence'].next_by_code('project.project')
        return super(AnalyticAccount, self).copy(default)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    vehicle_id = fields.Many2one(string="Vehicle", comodel_name="fleet.vehicle", compute="get_vehicle", store=True)
    subcontractor_partner_id = fields.Many2one(string="Subcontractor", comodel_name="res.partner")

    @api.onchange('task_id')
    def get_task_name(self):
        if self.task_id:
            self.name = self.task_id.name
            
    @api.depends('account_id')
    def get_vehicle(self):
        vehicle_obj = self.env['fleet.vehicle']
        for line in self:
            vehicle_id = vehicle_obj.search([('analytic_account_id', '=', line.account_id.id)])
            if vehicle_id:
                line.vehicle_id = vehicle_id.id
