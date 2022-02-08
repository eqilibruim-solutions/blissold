# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers import main

from odoo import fields    

import logging

_logger = logging.getLogger(__name__)


class WebsiteSale(main.WebsiteSale):

    @http.route(['/shop/area_infos/<model("res.country.state"):state>'], type='json', auth="public", methods=['POST'], website=True)
    def area_infos(self, state, **kw):
        areas = request.env['delivery.area'].search([('state_id','=',state.id)])
        return dict(
            areas=[(0,'Select Area')]+[(area.id, area.name) for area in areas],
        )

    def checkout_form_validate(self, mode, all_form_values, data):

        error = dict()
        error_message = []

        if data.get("city_id"):
            data["city_id"] = data.get("city_id")
        if mode == ('edit', 'billing'):
            data['state_id'] = False

        standard_error, standard_error_message = super(WebsiteSale, self).checkout_form_validate(
            mode, all_form_values, data
        )

        error.update(standard_error)
        error_message += standard_error_message
        country = request.env['res.country'].browse(int(data.get('country_id')))
        _logger.info(mode)
        _logger.info(request.env.company.country_id.code)
        _logger.info(country.code)
        if mode == ('edit', 'shipping') and request.env.company.country_id.code == country.code:
            state_id = int(data.get('state_id', 0))
            areas = request.env['delivery.area'].search([('state_id','=',state_id)])
            _logger.info(areas)
            if areas and (data.get("city_id") == 0 or not data.get('city_id')):
                error["city_id"] = "missing"
                error_message.append("Please Select Area")
        return error, error_message

    @http.route(['/shop/use_same_address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def use_same_address(self, **kw):
        order = request.website.sale_get_order()
        error = dict()
        error_message = []
        partner = order.partner_id
        country = order.partner_id.country_id

        if request.env.company.country_id.code == country.code:
            state_id = partner.state_id
            areas = request.env['delivery.area'].search([])
            if areas and not partner.city_id:
                error["city_id"] = "missing"
                error_message.append("Please Select Area")
                partner.state_id = False
        order.partner_shipping_id = order.partner_id.id
        _logger.info("Areas %s"%partner.city_id)
        _logger.info("Areas %s"%areas)
        _logger.info("Error %s"%error)
        if error:
            return request.redirect('/shop/address?partner_id=%d' % order.partner_id.id)
        return request.redirect(kw.get('callback') or '/shop/confirm_order')

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        def_country_id = order.partner_id.country_id
        def_city_id = order.partner_id.city_id

        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else: # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)
            if post.get('city_id') == 0: post['city_id']=False
            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.onchange_partner_id()
                    # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
                    order.partner_invoice_id = partner_id
                    if not kw.get('use_same'):
                        kw['callback'] = kw.get('callback') or \
                            (not order.only_services and (mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')
        if mode[1] == 'shipping':
            delivery_carrier = request.env['delivery.carrier'].sudo().search([('website_published', '=', True)],limit=1)
            if delivery_carrier.country_ids:
                def_country_id = delivery_carrier.country_ids and delivery_carrier.country_ids[0]

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(int(values['country_id']))
        country = country and country.exists() or def_country_id
        city = 'city_id' in values and values['city_id'] not in [0,''] and request.env['delivery.area'].browse(int(values['city_id']))
        city = city and city.exists() or def_city_id
        _logger.info(city)
        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'city': city,
            'cities': [],
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            'states': country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
        }
        return request.render("website_sale.address", render_values)

    def _get_mandatory_shipping_fields(self):
        return ["name", "street", "country_id", "mobile"]

    def _get_mandatory_billing_fields(self):
        return ["name", "street", "country_id", "email", "mobile"]

