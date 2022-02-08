# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockNotify(models.Model):
    _name = 'stock.notify'
    _description = 'Website Stock Notify'
    _inherit = ['mail.thread']

    @api.model
    def _cron_mail_stock_notify(self):
        notify_obj = self.env['stock.notify']
        template = self.env.ref(
            'website_stock_notify_73lines.product_notification_template')
        products_notify = notify_obj.search([])
        for product_notify in products_notify:
            qty_available = int(product_notify.product.qty_available)
            if qty_available > 0 and product_notify.state == 'draft':
                template.sudo().send_mail(product_notify.id, force_send=True)
                product_notify.write({'state': 'done'})
        return True

    @api.multi
    def cancel_notification(self):
        self.ensure_one()
        self.write({'state': 'cancel'})

    @api.multi
    def _get_product_url(self):
        prod_name = self.product.product_tmpl_id.name.replace(' ', '-')
        prod_id = self.product.product_tmpl_id.id
        self.product_url = 'shop/product/' + prod_name + '-' + str(prod_id)

    name = fields.Char(string='Record Title')
    product = fields.Many2one('product.product', string='Product')
    product_url = fields.Char(compute='_get_product_url', string='Product URL')
    email = fields.Char(srting='Email')
    created_on = fields.Datetime(string='Register Date')
    state = fields.Selection([('draft', 'Draft'),
                              ('cancel', 'Cancel'),
                              ('done', 'Done')],
                             string='Status', required=True, readonly=True,
                             default='draft')
