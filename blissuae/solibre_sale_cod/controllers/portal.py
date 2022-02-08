###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import http, _
from odoo.exceptions import AccessError
from odoo.http import request
try:
    from odoo.addons.sale.controllers.portal import CustomerPortal
except ImportError:
    CustomerPortal = object

import logging

_logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):


    MANDATORY_DELIVERY_FIELDS = ["dest_partner_name", "mobile", "dest_street", "country_id"]
    OPTIONAL_DELIVERY_FIELDS = ["state_id", "dest_makani_number", "dest_partner_longitude", "dest_partner_latitude"]
    @http.route([
        '/my/order/edit/<int:order>',
    ], type='http', auth='user', website=True)
    def portal_order_edit(self, order, access_token=None):
        try:
            order_sudo = self._document_check_access('sale.order', order, access_token=access_token)
        except AccessError:
            return request.redirect('/my')
        request.session['sale_order_id'] = order_sudo.id
        order_sudo.write({'state': 'draft'})
        return request.redirect('/shop/cart')

    @http.route([
        '/my/order/cancel/<int:order>',
    ], type='http', auth='user', website=True)
    def portal_order_cancel(self, order, access_token=None):
        try:
            order_sudo = self._document_check_access('sale.order', order, access_token=access_token)
        except AccessError:
            return request.redirect('/my')
        request.session['sale_order_id'] = order_sudo.id
        order_sudo.action_cancel()
        return request.redirect('/my/quotes')


    @http.route(['/deladd/<int:order_id>'], type='http', auth='public', website=True)
    def sale_update_address(self, order_id, access_token=None, **post):
        if not access_token:
            access_token = post.get('access_token')
        try:
            order = self._document_check_access('sale.order', order_id, access_token=access_token)
        except:
            raise AccessError("Incorrect Access Token")
        values = {
            'error': {},
            'error_message': [],
        }

        if post and request.httprequest.method == 'POST':
            error = False
            # error, error_message = self.details_form_validate(post)
            # values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_DELIVERY_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_DELIVERY_FIELDS})

                values.update({'dest_country_id': int(values.pop('country_id', 0))})

                if values.get('state_id') == '':
                    values.update({'dest_state_id': False})
                else:
                    values.update({'dest_state_id': values.pop('state_id')})

                order.sudo().write(values)
                if values.get("dest_makani_number"):
                    order.get_dest_makani()
                    if order.dest_partner_longitude and order.dest_partner_latitude:
                        return request.redirect('/address-thank-you')
                    else:
                        values.update({'error': 'Makani Incorrect', 'error_message': ['Makani number mis matched']})                        
                else:
                    return request.redirect('/address-thank-you')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'order': order,
            'countries': countries,
            'states': states,
            'access_token':access_token
        })

        response = request.render("solibre_sale_cod.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response