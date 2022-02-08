###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import http, _
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import WebsiteSaleForm
from odoo.exceptions import ValidationError

from odoo.http import request
import datetime
import json
from odoo import fields    
import logging

_logger = logging.getLogger(__name__)

class WebsiteSaleForm(WebsiteSaleForm):

    @http.route()
    def website_form_saleorder(self, **kwargs):
        model_record = request.env.ref('sale.model_sale_order')
        try:
            data = self.extract_data(model_record, kwargs)
        except ValidationError as e:
            return json.dumps({'error_fields': e.args[0]})
        time_slot = data['record'].get('time_slot')
        pref_date = data['record'].get('pref_date')

        if pref_date and not time_slot:
            return json.dumps({'error_fields': { 'pref_date': 'Delivery slot unavailable, please select another date'}})
        return super(WebsiteSaleForm, self).website_form_saleorder(**kwargs)

class WebsiteSale(WebsiteSale):

    @http.route(['/shop/timeslots/<int:day>/<int:month>/<int:year>'], type='json', auth="public", methods=['POST'], website=True)
    def timeslots(self, day=False, month=False, year=False, **kw):
        order = request.website.sale_get_order(force_create=1)
        today = fields.Datetime.now(self)
        if not day or (today.day == day and today.month == month and today.year==year):
            day_name = datetime.datetime.now().strftime('%A').lower()
            hour = today.hour
            domain = [('hour', '>', hour+4), ('days.name', '=', day_name)]
            slots = request.env['delivery.time.slot'].sudo().search(domain)
        else:
            day_name = datetime.date(year, month, day).strftime('%A').lower()
            slots = request.env['delivery.time.slot'].sudo().search([('days.name', '=', day_name)])
        if day and month and year:
            to_remove = request.env['delivery.time.slot']
            for slot in slots:
                max_orders_reached = request.env['sale.order.limit'].max_orders_reached(datetime.date(year, month, day).strftime("%Y-%m-%d"), order, slot)
                if max_orders_reached:
                    to_remove += slot
            slots = slots - to_remove
        slots = dict(slots=[(slot.id, slot.name) for slot in slots],)
        return slots

    @http.route()
    def check_field_validations(self, values):
        res = super(WebsiteSale, self).check_field_validations(values)
        if 'commitment_date' not in values or not values['commitment_date']:
            return res
        order = request.website.sale_get_order(force_create=1)
        post_commitment_date = values['commitment_date']
        if post_commitment_date < datetime.datetime.now().strftime("%Y-%m-%d"):
            res['error'].append(
                _('Desired date must be later than current one.'))
            return res
        if post_commitment_date < order.expected_date.strftime("%Y-%m-%d"):
            res['error'].append(
                _('Desired date must be later than expected '
                  'date \'%s\'.') % (
                    order.expected_date.strftime('%d/%m/%Y')))
            return res
        order['commitment_date'] = post_commitment_date
        return res

    @http.route()
    def extra_info(self, **post):
        # Check that this option is activated
        extra_step = request.website.viewref('website_sale.extra_info_option')
        if not extra_step.active:
            return request.redirect("/shop/payment")

        # check that cart is valid
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        # if form posted
        if 'post_values' in post:
            values = {}
            for field_name, field_value in post.items():
                if field_name in request.env['sale.order']._fields and field_name.startswith('x_'):
                    values[field_name] = field_value
            if values:
                order.write(values)
            return request.redirect("/shop/payment")

        values = {
            'website_sale_order': order,
            'post': post,
            'escape': lambda x: x.replace("'", r"\'"),
            'partner': order.partner_id.id,
            'order': order,
            'time_slots': self.timeslots(),
            'time_slot': order.time_slot.id
        }

        return request.render("website_sale.extra_info", values)