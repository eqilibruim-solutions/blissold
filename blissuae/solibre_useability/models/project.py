from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)


class Project(models.Model):
    _inherit = 'project.project'

    crm_lead_id = fields.Many2one(string="Lead", comodel_name="crm.lead")
    code = fields.Char(string='Project Number', related="analytic_account_id.code")

    def _plan_get_stat_button(self):
        stat_buttons = super(Project, self)._plan_get_stat_button()
        if self.env.user.has_group('purchase.group_purchase_user'):
            # read all the sale orders linked to the projects' tasks
            pol = self.env['purchase.order.line'].search([('account_analytic_id','=',self.analytic_account_id.id)])
            purchase_orders = pol.mapped('order_id')
            if purchase_orders:
                stat_buttons.append({
                    'name': _('Purchase Orders'),
                    'count': len(purchase_orders),
                    'icon': 'fa fa-credit-card',
                    'action': _to_action_data(
                        action=self.env.ref('purchase.purchase_form_action'),
                        domain=[('id', 'in', purchase_orders.ids)],
                        context={'create': False, 'edit': False, 'delete': False}
                    )
                })

                invoice_ids = self.env['purchase.order'].search_read([('id', 'in', purchase_orders.ids)], ['invoice_ids'])
                invoice_ids = list(itertools.chain(*[i['invoice_ids'] for i in invoice_ids]))
                invoice_ids = self.env['account.move'].search_read([('id', 'in', invoice_ids), ('type', '=', 'in_invoice')], ['id'])
                invoice_ids = list(map(lambda x: x['id'], invoice_ids))

                if invoice_ids:
                    stat_buttons.append({
                        'name': _('Bills'),
                        'count': len(invoice_ids),
                        'icon': 'fa fa-pencil-square-o',
                        'action': _to_action_data(
                            action=self.env.ref('account.action_move_in_invoice_type'),
                            domain=[('id', 'in', invoice_ids), ('type', '=', 'in_invoice')],
                            context={'create': False, 'delete': False}
                        )
                    })
        expenses = self.env['hr.expense'].search([('analytic_account_id','=',self.analytic_account_id.id)])
        if expenses:
            stat_buttons.append({
                'name': _('Expenses'),
                'count': len(expenses),
                'icon': 'fa fa-dollar',
                'action': _to_action_data(
                    action=self.env.ref('hr_expense.hr_expense_actions_all'),
                    domain=[('id', 'in', expenses.ids)],
                    context={'create': False, 'delete': False}
                )
            })
        return stat_buttons
