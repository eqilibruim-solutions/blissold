# Copyright 2015 Antiun Ingeniería, S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


    

class RequireLoginToCheckout(WebsiteSale):
    @http.route(auth="user")
    def checkout(self, **post):
        return super().checkout(**post)

class AuthSignupHome(AuthSignupHome):

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        _logger.info(qcontext)
        values = { key: qcontext.get(key) for key in ('login', 'name', 'password', 'mobile') }
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '').split('_')[0]
        if lang in supported_lang_codes:
            values['lang'] = lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()
