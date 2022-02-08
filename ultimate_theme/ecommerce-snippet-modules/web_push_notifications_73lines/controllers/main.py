# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

import json
import odoo
from odoo import http
from odoo.http import request


class OneSignal(odoo.addons.web.controllers.main.Home):

    @http.route(['/manifest.json'], type='http', auth='public', website=True)
    def one_signal_manifest(self, **post):
        current_website = request.website
        content = {
            "name": current_website.onesignal_site_name,
            "short_name": current_website.onesignal_site_short_name,
            "start_url": "/",  # Don't change!
            "display": "standalone",  # Don't change!
            "gcm_sender_id": "482941778795"  # Don't change!
        }
        return request.make_response(json.dumps(content))

    @http.route(['/OneSignalSDKWorker.js'], type='http',
                auth='public', website=True)
    def one_signal_sdk_worker(self, **post):
        mimetype = 'application/javascript'
        content = "importScripts" \
                  "('https://cdn.onesignal.com/sdks/OneSignalSDK.js');"
        return request.make_response(content, [('Content-Type', mimetype)])

    @http.route(['/OneSignalSDKUpdaterWorker.js'], type='http',
                auth='public', website=True)
    def one_signal_sdk_updater_worker(self, **post):
        mimetype = 'application/javascript'
        content = "importScripts" \
                  "('https://cdn.onesignal.com/sdks/OneSignalSDK.js');"
        return request.make_response(content, [('Content-Type', mimetype)])
