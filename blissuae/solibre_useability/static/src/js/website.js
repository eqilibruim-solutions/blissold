odoo.define('solibre_useability.checkout', function (require) {
'use strict';

var core = require('web.core');
var publicWidget = require('web.public.widget');

var _t = core._t;

publicWidget.registry.websiteSaleDeliveryLocation = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
        'change select[name="pickup_location"]': '_onSetLocation',
    },

    _onSetLocation: function (ev) {
        var value = $(ev.currentTarget).val();
        this._rpc({
            route: '/shop/update_delivery_location',
            params: {
                pickup_location: value,
            }});
    },
});
});
