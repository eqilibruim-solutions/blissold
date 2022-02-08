# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

import logging
import urllib
import requests
import json
import datetime

_logger = logging.getLogger(__name__)

class DeliveryTimeSlot(models.Model):
    _name = 'delivery.time.slot'
    _description = 'Delivery Time Slot'

    name = fields.Char(string="Time Slot")
    hour = fields.Float(string="Hour of the day")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    team_id = fields.Many2one('crm.team', 'Sales Team', check_company=False)
    schedule_id = fields.Many2one(string="Delivery Schedule", comodel_name="delivery.schedule",copy=False)
    pickup_schedule_id = fields.Many2one(string="Delivery Schedule", comodel_name="delivery.schedule", copy=False)
    mobile = fields.Char(string="Mobile", related="partner_shipping_id.mobile")
    city_id = fields.Many2one(string="City", comodel_name="delivery.area", related="partner_shipping_id.city_id", store=True)
    is_cod = fields.Boolean(string="Cash on delivery?", compute="get_is_cod", store=True)
    mobile = fields.Char(string="Mobile",copy=False)
    cod_amount = fields.Float(string="COD Amount", compute="get_amount_due")
    delivered = fields.Boolean(string="Delivered", copy=False)
    picked_up = fields.Boolean(string="Picked", copy=False)
    location = fields.Char(string="Current location", related="schedule_id.location")
    location_url = fields.Char(string="Location Url", copy=False)
    partner_latitude = fields.Float('Geo Latitude', digits=(16, 5), copy=False)
    partner_longitude = fields.Float('Geo Longitude', digits=(16, 5), copy=False)
    dest_makani_number = fields.Char(string="Makani delivery", copy=False)
    dest_location_url = fields.Char(string="Delivery Location", compute="get_location_url")
    dest_partner_latitude = fields.Float('Geo Latitude', digits=(16, 5), copy=False)
    dest_partner_longitude = fields.Float('Geo Longitude', digits=(16, 5), copy=False)
    dest_partner_name = fields.Char(string="Delivery address", copy=False)
    dest_street = fields.Char('Delivery Street', copy=False)
    dest_street2 = fields.Char('Delivery Street2', copy=False)
    dest_zip = fields.Char('Delivery Zip', change_default=True)
    dest_city_id = fields.Many2one(string='Delivery City', comodel_name="delivery.area", copy=False)
    dest_area_id = fields.Many2one(string='Delivery Area', comodel_name="delivery.area", copy=False)
    dest_sorting = fields.Char(string="Sorting Number", related="dest_area_id.sorting", store=True)
    dest_state_id = fields.Many2one("res.country.state", string='Delivery State', copy=False)
    dest_country_id = fields.Many2one('res.country', string='Delivery Country', copy=False)
    dest_mobile = fields.Char(string="Delivery Mobile", related="partner_shipping_id.mobile")
    sale_order_tracking_ids = fields.One2many(string="Tracking", comodel_name="sale.order.tracking", inverse_name="order_id", copy=False)
    last_track = fields.Char(string="Last track",compute="get_last_track")
    status_count = fields.Integer(string="Count", compute="get_status_count")
    pref_date = fields.Date(string="Delivery date", copy=False)
    preferred_delivery_date = fields.Date(string="Preferred delivery date", copy=False)
    time_slot = fields.Many2one(string="Time slot", comodel_name="delivery.time.slot", copy=False)
    preferred_delivery_time_slot_id = fields.Many2one(string="Time slot", comodel_name="delivery.time.slot", copy=False)
    short_url = fields.Char(string="Shorl URL", copy=False)
    prepared_by = fields.Many2one(string="Prepared by", comodel_name="res.users", copy=False)
    accepted_by = fields.Many2one(string="Accepted by", comodel_name="res.users", copy=False)
    driver_id = fields.Many2one(string="Driver", comodel_name="res.users", compute="get_driver", store=True)
    shipping_state = fields.Selection(string="Shipping state",
                                      default='new',
                                      copy=False,
                                      selection=[('to_pickup', 'Ready for pickup'),
                                                 ('picked_up', 'Picked up'),
                                                 ('arrived_facility', 'Arrived at facility'),
                                                 ('exception', 'Exception'),
                                                 ('new', 'New Order'),
                                                 ('accepted', 'Accepted'),
                                                 ('to_deliver', 'To deliver'),
                                                 ('dispatched', 'Out for delivery'),
                                                 ('delivered', 'Delivered'),
                                                 ('rto', 'RTO'),
                                                 ('returned', 'Returned'),])
    delivery_zone_id = fields.Many2one(string="Delivery Zone", comodel_name="delivery.zone", compute="get_delivery_zone", store=True)
    delivery_area_id = fields.Many2one(string="Delivery Area", comodel_name="delivery.area", compute="get_delivery_zone", store=True)
    pickup_location_id = fields.Many2one(string="Pickup Location", comodel_name="res.company", copy=False)
    origin_sale_id = fields.Many2one(string="Related Sale id", comodel_name="sale.order")

    def _check_carrier_quotation(self, force_carrier_id=None):
        self.ensure_one()
        res = super(SaleOrder, self)._check_carrier_quotation(force_carrier_id)
        if self.carrier_id and self.carrier_id.pickup_location_id:
            self.pickup_location_id = self.carrier_id.pickup_location_id.id
        self.get_delivery_zone()
        return res

    def action_payment_transaction(self):
        action = self.env.ref('payment.action_payment_transaction').read()[0]
        action['domain'] = [('id', 'in', self.transaction_ids.ids)]
        return action

    @api.depends('schedule_id')
    def get_driver(self):
        for order in self:
            driver_id = False
            vehicle_id = False
            if order.schedule_id and order.schedule_id.driver_id:
                if order.schedule_id.driver_id.user_ids:
                    driver_id = order.schedule_id.driver_id.user_ids[0].id
                    vehicle_id = order.schedule_id.vehicle_id.id
            order.driver_id = driver_id
            order.vehicle_id = vehicle_id

    @api.depends('partner_shipping_id', 'pickup_location_id')
    def get_delivery_zone(self):
        for order in self:
            if order.partner_shipping_id.city_id:
                order.update({'delivery_area_id': order.partner_shipping_id.city_id.id,
                             'partner_longitude': order.partner_shipping_id.city_id.center_longitude,
                             'partner_latitude': order.partner_shipping_id.city_id.center_latitude})
            if order.pickup_location_id:
                order.delivery_zone_id = order.pickup_location_id.partner_id.delivery_zone_id.id
            else:
                order.delivery_zone_id = order.delivery_area_id and order.delivery_area_id.zone_id.id or False
            if order.website_id and order.delivery_zone_id.team_id:
                order.user_id = order.delivery_zone_id.team_id.user_id.id
                order.team_id = order.delivery_zone_id.team_id.id
            order.picking_ids.delivery_zone_id = order.delivery_zone_id.id

    def set_prepared(self):
        track = self.env['sale.order.tracking'].create({
            'activity_id': self.env.ref('solibre_sale_cod.sale_order_tracking_activity_prepared').id,
            'state_id': self.env.ref('solibre_sale_cod.tracking_activity_state_prepared_success').id,
            'order_id': self.id})
        self.write({'shipping_state': 'to_deliver',
                    'prepared_by': self.env.user.id})

    def set_accepted(self):
        if self.company_id.auto_signup and self.website_id:
            self.partner_id.auto_signup()
        track = self.env['sale.order.tracking'].create({
            'activity_id': self.env.ref('solibre_sale_cod.sale_order_tracking_activity_accepted').id,
            'state_id': self.env.ref('solibre_sale_cod.tracking_activity_state_accepted_success').id,
            'order_id': self.id})
        self.write({'accepted_by': self.env.user.id, 
                    'shipping_state': 'accepted'})

    def set_dispatched(self):
        track = self.env['sale.order.tracking'].create({
            'activity_id': self.env.ref('solibre_sale_cod.sale_order_tracking_activity_delivery').id,
            'state_id': self.env.ref('solibre_sale_cod.tracking_activity_state_delivery_dispatched').id,
            'order_id': self.id})
        self.shipping_state = 'dispatched'

    def set_scheduled(self):
        for order in self:
            track = self.env['sale.order.tracking'].create({
                'activity_id': self.env.ref('solibre_sale_cod.sale_order_tracking_activity_delivery').id,
                'state_id': self.env.ref('solibre_sale_cod.tracking_activity_state_delivery_scheduled').id,
                'order_id': order.id})

    def set_delivered(self): 
        pickings = self.sudo().picking_ids.filtered(lambda p:p.state not in ('done', 'cancel'))
        for pick in pickings:
            for line in pick.move_lines:
                line.write({'quantity_done': line.product_uom_qty})
            pick.action_assign()
            pick.action_done()
        self.write({'shipping_state': 'delivered',
                    'delivered': True})
        self.send_delivered_mail()
        return True

    def send_delivered_sms(self):
        for sale in self:
            sale._message_sms_with_template(
                                template=self.env.ref('solibre_sale_cod.sms_template_data_delivery_confirmation'),
                                partner_ids=sale.partner_id.ids,
                                put_in_queue=False)
        return True

    def send_delivered_mail(self):
        for sale in self:
            if sale.partner_id.email:
                try:
                    delivery_template_id = self.env.ref('solibre_sale_cod.mail_template_data_delivery_confirmation')
                    sale.with_context(force_send=True).message_post_with_template(delivery_template_id.id, email_layout_xmlid='mail.mail_notification_light')
                except:
                    continue
        return True

    def get_location_url(self):
        for sale in self:
            if sale.partner_longitude and sale.partner_latitude:
                lng = sale.partner_longitude
                lat = sale.partner_latitude
                sale.location_url = 'https://www.google.com/maps/dir/Current+Location/%s,%s'%(lat,lng)
            else:
                sale.location_url = ''
            if sale.dest_partner_longitude and sale.dest_partner_latitude:
                lng = sale.dest_partner_longitude
                lat = sale.dest_partner_latitude
                sale.dest_location_url = 'https://www.google.com/maps/dir/Current+Location/%s,%s'%(lat,lng)
            else:
                sale.dest_location_url = ''

    @api.depends('sale_order_tracking_ids')
    def get_last_track(self):
        for order in self:
            if order.sale_order_tracking_ids:
                track = order.sale_order_tracking_ids[0]
                order.last_track = "%s : %s"%(track.activity_id.name, track.state_id.name)
            else:
                order.last_track = False

    def force_delivery(self):
        self.write({'shipping_state': 'to_deliver'})
        activity_id = self.env.ref('solibre_sale_cod.sale_order_tracking_activity_address_update')
        state_id = self.env.ref('solibre_sale_cod.tracking_activity_state_address_update_agent')
        track = self.env['sale.order.tracking'].create({'activity_id': activity_id.id,
                                                        'state_id': state_id.id,
                                                        'order_id': self.id})

    @api.onchange('dest_makani_number')
    def get_dest_makani(self):
        url = 'https://www.makani.ae/MakaniPublicDataService/MakaniPublic.svc/GetMakaniDetails?makanino='
        for order in self:
            if order.dest_makani_number:
                makani_number = urllib.parse.quote_plus(order.dest_makani_number)
                url = '%s%s'%(url,makani_number)
                result = requests.get(url)
                result = json.loads(result.text)
                result = json.loads(result)
                makani_info = result.get('MAKANI_INFO')
                _logger.info(result)
                if makani_info:
                    lat, lng = makani_info[0].get('LATLNG').split(',')
                    order.update({'dest_partner_longitude': lng,
                                  'dest_partner_latitude': lat})

    def get_delivery_address_url(self):
        """
            Get a portal url for this model, including access_token.
            The associated route must handle the flags for them to have any effect.
            - suffix: string to append to the url, before the query string
            - report_type: report_type query string, often one of: html, pdf, text
            - download: set the download query string to true
            - query_string: additional query string
            - anchor: string to append after the anchor #
        """
        self.ensure_one()
        if self.short_url:
            return self.short_url
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = '%s/deladd/%s?access_token=%s' % (
            base_url,
            self.id,
            self._portal_ensure_token()
        )
        linkRequest = {"destination": url, 
                       "domain": { "fullName": "tmx.simplyodoo.me" }}
        requestHeaders = {"Content-type": "application/json",
                          "apikey": "be7a256a74f84336ac495b260e2fc0fa",
                          "workspace": "864569c1f6d94d51ab836ad08b4ee33a"}
        r = requests.post("https://api.rebrandly.com/v1/links",
                          data=json.dumps(linkRequest),
                          headers=requestHeaders)
        if (r.status_code == requests.codes.ok):
            link = r.json()
            url = 'http://%s' % link["shortUrl"]
            self.short_url = url
            _logger.info(self.short_url)
        return url


    def get_status_count(self):
        for order in self:
            if order.sale_order_tracking_ids:
                order.status_count = len(order.sale_order_tracking_ids)
            else:
                order.status_count = 0

    def send_delivery_message(self):
        action = self.env.ref('sms.sms_composer_action_form')
        template = self.env.ref('solibre_sale_cod.sms_template_delivery')
        action = action.read()[0]
        action['context'] = {'destination': 1,
                             'default_number_field_name': 'dest_mobile',
                             'default_template_id' : template.id,
                             'default_composition_mode': 'guess',
                             'default_res_ids': self.ids,
                             'default_res_id': self.id}
        return action


    def _sms_get_default_partners(self):
        """ This method will likely need to be overridden by inherited models.
               :returns partners: recordset of res.partner
        """
        return False
        partners = self.env['res.partner']
        if self.env.context.get('destination'):
            partners = self.mapped('partner_shipping_id')
        else:
            for fname in self._sms_get_partner_fields():
                partners |= self.mapped(fname)
        return partners

    @api.onchange('partner_id')
    def set_mobile(self):
        self.ensure_one()
        if self.partner_id:
            self.mobile = self.partner_id.mobile
            self.location_url = self.partner_id.location_url
            self.partner_latitude = self.partner_id.partner_latitude
            self.partner_longitude = self.partner_id.partner_longitude

    def confirm_pickup(self):
        self.picked_up = True

    def write(self, vals):
        # if 'schedule_id' in vals:
        #     if vals.get('schedule_id') == False:
        #         for invoice in self.invoice_ids:
        #             stmtl = self.env['account.bank.statement.line'].search([('name','=',invoice.name)])
        #             if stmtl:
        #                 stmtl.unlink()
        tracking_obj = self.env['sale.order.tracking']
        force_user = self._context.get('force_user')
        if force_user:
            tracking_obj = tracking_obj.with_user(force_user)
        if vals.get('dest_partner_latitude') and vals.get('dest_partner_longitude'):
            vals.update({'shipping_state': 'to_deliver'})
        if vals.get('dest_makani_number'):
            activity_id = self.env.ref('solibre_sale_cod.sale_order_tracking_activity_address_update')
            state_id = self.env.ref('solibre_sale_cod.tracking_activity_state_address_update_makani')
            track = tracking_obj.create({'activity_id': activity_id.id,
                                         'state_id': state_id.id,
                                         'order_id': self.id})
        if vals.get('pref_date') and self.picking_ids:
            self.picking_ids.filtered(lambda l:l.state not in ['done', 'cancel']).write({'pref_date': vals.get('pref_date')})
        if vals.get('time_slot') and self.picking_ids:
            self.picking_ids.filtered(lambda l:l.state not in ['done', 'cancel']).write({'time_slot': vals.get('time_slot')})

        if vals.get('shipping_state'):
            ICPSudo = self.env['ir.config_parameter'].sudo()
            franchise_url = ICPSudo.get_param('franchise_url')
            if franchise_url == "False":
                franchise_url = False
            if franchise_url and self.website_id:
                url = '%s/update/%s/%s'%(franchise_url,self.name,vals.get('shipping_state'))
                result = requests.get(url)
            elif self.sudo().origin_sale_id:
                self.sudo().origin_sale_id.update_main_order_status(vals.get('shipping_state'))

        return super(SaleOrder, self).write(vals)

    def update_main_order_status(self, state):
        order = self.sudo()
        order = order.with_context(force_user=order.user_id.id)
        order.write({'shipping_state': state})
        if state == 'accepted':
            order.franchise_reinvoice()

    def get_amount_due(self):
        for sale in self:
            if sale.is_cod and sale.invoice_ids:
                invoiced_residual_amount = sum(sale.invoice_ids.mapped('amount_residual'))
                sale.cod_amount = invoiced_residual_amount
            elif sale.is_cod and not sale.invoice_ids:
                sale.cod_amount = sale.amount_total
            else:
                sale.cod_amount = 0

    @api.depends('transaction_ids')
    def get_is_cod(self):
        for sale in self:
            cod = []
            for transaction in sale.transaction_ids:
                cod.append(transaction.acquirer_id.journal_id.is_cod)
            sale.is_cod = any(cod)
        return True

    def franchise_reinvoice(self):
        for order in self:
            for picking in order.picking_ids:
                picking.action_cancel()
            for invoice in order.invoice_ids:
                invoice._franchise_create_invoices()

    @api.model
    def _create_subsidiary_order(self, company):
        processed_orders = self.sudo().search([('company_id', '=', company.id),
                                               ('website_id', '!=', False),
                                               ('date_order', '>=', fields.Date.today())])
        sales_domain = [('website_id', '!=', False),
                        ('state', '=', 'sale'),
                        ('shipping_state', '=', 'new'),
                        ('company_id', '!=', company.id),
                        ('team_id.company_id', '=', company.id),
                        ('date_order', '>=', fields.Date.today()),
                        ('name', 'not in', processed_orders.mapped('name'))]
        orders = self.search(sales_domain)
        for order in orders:
            order.franchise_create_sale_order(company)

    def create_cod_transaction(self):
        if not self.transaction_ids:
            acquirer_id = self.env['payment.acquirer'].search([('company_id', '=', self.company_id.id),
                                                               ('journal_id.is_cod', '=', True)], limit=1)
            vals = {'acquirer_id': acquirer_id and acquirer_id.id or False}
            self._create_payment_transaction(vals)


    def franchise_create_sale_order(self, company):
        """ Create a Sales Order from the current PO (self)
            Note : In this method, reading the current PO is done as sudo, and the creation of the derived
            SO as intercompany_user, minimizing the access right required for the trigger user.
            :param company : the company of the created PO
            :rtype company : res.company record
        """
        return


    def _prepare_sale_order_data(self, name, partner, company):
        """ Generate the Sales Order values from the PO
            :param name : the origin client reference
            :rtype name : string
            :param partner : the partner reprenseting the company
            :rtype partner : res.partner record
            :param company : the company of the created SO
            :rtype company : res.company record
            :param direct_delivery_address : the address of the SO
            :rtype direct_delivery_address : res.partner record
        """
        self.ensure_one()
        warehouse = company.warehouse_id and company.warehouse_id.company_id.id == company.id and company.warehouse_id or False
        if not warehouse:
            raise Warning(_('Configure correct warehouse for company(%s) from Menu: Settings/Users/Companies' % (company.name)))

        return {
        }

    @api.model
    def _prepare_sale_order_line_data(self, line, company, sale_id):
        """ Generate the Sales Order Line values from the PO line
            :param line : the origin Purchase Order Line
            :rtype line : purchase.order.line record
            :param company : the company of the created SO
            :rtype company : res.company record
            :param sale_id : the id of the SO
        """
        # it may not affected because of parallel company relation
        price = line.price_unit or 0.0
        taxes = line.tax_id
        if line.product_id:
            taxes = line.product_id.taxes_id
        company_taxes = [tax_rec for tax_rec in taxes if tax_rec.company_id.id == company.id]
        if sale_id:
            so = self.env["sale.order"].sudo().browse(sale_id)
            company_taxes = so.fiscal_position_id.map_tax(company_taxes, line.product_id, so.partner_id)
        quantity = line.product_id and line.product_uom._compute_quantity(line.product_qty, line.product_id.uom_id) or line.product_qty
        price = line.price_unit
        return {
        }



    def create_cash_statement_lines(self,schedule_id):
        return


