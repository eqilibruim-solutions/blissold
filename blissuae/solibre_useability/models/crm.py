# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

import logging

_logger = logging.getLogger(__name__)

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    analytic_account_id = fields.Many2one(string="Analytic Account", comodel_name="account.analytic.account")

    def create_analytic(self):
        if not self.analytic_account_id:
            self.analytic_account_id = self.env['account.analytic.account'].create({'name':self.name}).id

    @api.model
    def create(self, vals):
        res = super(CrmTeam, self).create(vals)
        res.create_analytic()
        return res

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def _compute_task_count(self):
        for lead in self:
            lead.task_count = len(lead.project_id.task_ids.filtered(lambda t:t.stage_id.fold == False or not t.stage_id))

    code = fields.Char(string='Lead Number', related="analytic_account_id.code", readonly=True, store=True)
    analytic_account_id = fields.Many2one(string="Analytic account", comodel_name="account.analytic.account")
    project_id = fields.Many2one(string="Project", comodel_name="project.project")
    task_count = fields.Integer(compute='_compute_task_count', string="Task Count")

    @api.onchange('stage_id')
    def create_project(self):
        if not self.partner_id:
            raise UserError(_("Customer not yet defined for this opportunity!"))
        name = self.name
        partner_id = self.partner_id.id
        if not self.analytic_account_id:
            project_id = self.env['project.project'].create({'crm_lead_id':self.id,
                                                             'name':name,
                                                             'allow_timesheets': True,
                                                             'company_id':self.env.user.company_id.id,
                                                             'privacy_visibility':'employees',
                                                             'partner_id':partner_id,})
            self.update({'analytic_account_id': project_id.analytic_account_id.id,
                        'project_id': project_id.id})
        if self.order_ids:
            self.order_ids.write({'analytic_account_id': project_id.analytic_account_id.id})
