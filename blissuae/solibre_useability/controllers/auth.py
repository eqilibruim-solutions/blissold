from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.phone_validation.tools import phone_validation
from odoo import http, _
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)


# class SignupVerifyMobile(AuthSignupHome):
#     @http.route()
#     def web_auth_signup(self, *args, **kw):
#         qcontext = self.get_auth_signup_qcontext()
#         mobile = request.params.get("mobile")
#         if mobile:
#             try:
#                 phone = data.get("mobile")
#                 country = request.env["res.country"].sudo().browse(data.get("country_id"))
#                 mobile = phone_validation.phone_format(
#                     phone,
#                     country.code if country else None,
#                     country.phone_code if country else None,
#                     force_format="INTERNATIONAL",
#                     raise_exception=True,
#                 )
#             except Exception as e:
#                 qcontext["error"] = _("Incorrect mobile number.")
#                 return request.render("auth_signup.signup", qcontext)
#         return super().web_auth_signup(*args, **kw)