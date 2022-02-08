from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)

class SaleTrackingWizard(models.TransientModel):
    _name = 'sale.tracking.wizard'
    _description = 'Sale Tracking Wizard'

    activity_id = fields.Many2one(string="Activity", comodel_name="sale.order.tracking.activity")
    state_id = fields.Many2one(string="State", comodel_name="sale.order.tracking.activity.state")
    cod_amount = fields.Float(string="COD Amount")
    attachment_ids = fields.Many2many('ir.attachment', string='Files')
    note = fields.Char(string="Comments")
    signature = fields.Char(string="Signature")    
    receiver_name = fields.Char(string="Receiver name")
    receiver_id_type = fields.Selection(string="ID Type", selection=[('eid', 'Emirates ID'),
                                                                    ('driving_licence', 'Driving Licence'),
                                                                    ('company_id', 'Company ID'),
                                                                    ('passport', 'Passport')])
    receiver_id = fields.Char(string="Receiver ID")

    def confirm(self):
        order = self.env['sale.order'].browse(self.env.context.get('active_id', False))
        if order:
            track = self.env['sale.order.tracking'].create({'activity_id': self.activity_id.id,
                                                    'state_id': self.state_id.id,
                                                    'note':self.note,
                                                    'order_id': order.id})
            values = { 'res_model': 'sale.order',
                       'res_id': order.id}
            for attachment in self.attachment_ids:
                attachment.copy(values)
            if self.state_id == self.env.ref('solibre_sale_cod.tracking_activity_state_delivery_success'):
                order.set_delivered()
            if self.state_id == self.env.ref('solibre_sale_cod.tracking_activity_state_pickup_success'):
                order.write({'shipping_state': 'picked_up'})
            if self.state_id == self.env.ref('solibre_sale_cod.tracking_activity_state_dispatched_success'):
                order.write({'shipping_state': 'dispatched'})
            if self.state_id == self.env.ref('solibre_sale_cod.tracking_activity_state_delivery_refused'):
                order.write({'shipping_state': 'rto'})
            if self.signature:
                order.write({'signature': self.signature})
            msg = ""
            if self.receiver_name:
                msg = "Received by"
                if self.receiver_name:
                    msg += " %s"%self.receiver_name
                if self.receiver_id:
                    msg += " %s"%self.receiver_id
                if self.receiver_id_type:
                    msg += " %s"%self.receiver_id_type.name
                msg +="\n"
            if self.note:
                msg += self.note
            if len(msg)>1:
                order.message_post(body=msg)
