# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import hashlib
import json

from odoo import api, models
from odoo.http import request
from odoo.tools import ustr

import odoo


class Http(models.AbstractModel):
    _inherit = 'ir.http'


    def session_info(self):
        session_info = super(Http, self).session_info()

        user = request.env.user
        version_info = odoo.service.common.exp_version()

        user_context = request.session.get_context() if request.session.uid else {}

        if self.env.user.has_group('base.group_user'):
            session_info.update({
                "user_companies": {'current_company': (user.company_id.id, user.company_id.shortname or user.company_id.name), 'allowed_companies': [(comp.id, comp.shortname or comp.name) for comp in user.company_ids]},
            })
        return session_info
