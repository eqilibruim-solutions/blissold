from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)


class HrLeaveReport(models.Model):
    _inherit = 'hr.leave.report'

    @api.model
    def action_time_off_analysis(self):
    	return