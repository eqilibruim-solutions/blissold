from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class DeliveryZone(models.Model):
    _inherit = 'delivery.zone'
    _description = 'Delivery Zone'

    vehicle_id = fields.Many2one(string="Vehicle", comodel_name="fleet.vehicle")
    team_id = fields.Many2one(string="Sales Team", comodel_name="crm.team")

class DeliverySchedule(models.Model):
    _name = 'delivery.schedule'
    _order = 'name desc'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'barcodes.barcode_events_mixin']
    _description = 'Delivery Schedule'

    name = fields.Char(string='Reference', copy=False, readonly=False, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    date = fields.Date(string="Date", default=fields.Date.context_today)
    tracking_status = fields.Char(string="Tracking Status")
    driver_id = fields.Many2one(string="Driver",
                                comodel_name="res.partner")
    vehicle_id = fields.Many2one(string="Vehicle",
                                comodel_name="fleet.vehicle")
    location = fields.Char(string="Location", related="vehicle_id.location")
    delivery_count = fields.Float(string="Delivered", compute="compute_delivered")
    delivered_count = fields.Float(string="Delivered", compute="compute_delivered")
    zone_id = fields.Many2one(string="Delivery Zone", comodel_name="delivery.zone")
    not_delivered_count = fields.Float(string="Not Delivered", compute="compute_delivered")
    order_ids = fields.One2many(string="Orders",
                                comodel_name="sale.order",
                                inverse_name="schedule_id")
    pickup_order_ids = fields.One2many(string="Orders",
                                comodel_name="sale.order",
                                inverse_name="pickup_schedule_id") 
    schedule_type = fields.Selection(string="Schedule type", 
                                     default="both",
                                     selection=[('both','Pickup and Delivery'),
                                                ('delivery','Delivery'),
                                                ('pickup','Pick-Up'),])
    state = fields.Selection(string="State", default='draft',
                                             selection=[('draft','Draft'),
                                                        ('open','In Progress'),
                                                        ('done','Done'),])

    @api.onchange('vehicle_id')
    def get_driver(self):
        if self.vehicle_id:
            self.driver_id = self.vehicle_id.driver_id.id
            self.order_ids.get_driver()

    def compute_delivered(self):
        for schedule in self:
            schedule.delivery_count = len(schedule.order_ids)
            schedule.delivered_count = len(schedule.order_ids.filtered(lambda l:l.shipping_state == 'delivered'))
            schedule.not_delivered_count = len(schedule.order_ids.filtered(lambda l:l.shipping_state != 'delivered'))

    @api.onchange('schedule_type')
    def _onchange_product_id(self):
        if not self.schedule_type:
            return
        if self.schedule_type == 'delivery':
            domain = {'order_ids': [('shipping_state', '=', 'to_deliver')]}
        elif self.schedule_type == 'delivery':
            domain = {'pickup_order_ids': [('shipping_state', '=', 'to_pickup')]}
        else:
            domain = {'pickup_order_ids': ['|',('shipping_state', '=', 'to_pickup'),('shipping_state', '=', 'to_deliver')]}
        return {'domain': domain}

    def on_barcode_scanned(self, barcode):
        order = self.env['sale.order'].search([('name','=',barcode)])
        if not order:
            return {'warning': {
                'title': _('Wrong barcode'),
                'message': _('The barcode "%(barcode)s" doesn\'t correspond to any shipping.') % {'barcode': barcode}
            }}
        elif len(order)>1:
            return {'warning': {
                'title': _('Too many shippings found'),
                'message': _('The barcode "%(barcode)s" doesn\'t correspond to a unique shipping.') % {'barcode': barcode}
            }}
        else:
            state = order.shipping_state
            _logger.info(state)


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('delivery.schedule') or _('New')
        result = super(DeliverySchedule, self).create(vals)
        return result

    def action_confirm(self):
        for order in self.order_ids:
            order.set_dispatched()
        self.write({'state':'open'})

    def action_done(self):
        for order in self.order_ids:
            for picking in order.picking_ids.filtered(lambda p:p.state not in ('done','cancel')):
                for line in picking.move_lines:
                    line.quantity_done = line.reserved_availability
                picking.button_validate()
            for payment in order.authorized_transaction_ids:
                if payment.acquirer_id.journal_id.is_cod:
                    payment._set_transaction_done()
                    payment._post_process_after_done()
        self.write({'state':'done'})


