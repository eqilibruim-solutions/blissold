odoo.define('website.snippets.options.inherit', function (require) {
'use strict';

var core = require('web.core');
var Dialog = require('web.Dialog');
var weWidgets = require('web_editor.widget');
var options = require('web_editor.snippets.options');

var _t = core._t;
var qweb = core.qweb;

options.registry.topMenuHide = options.Class.include({

    hide: function () {
        var self = this;
        this.trigger_up('action_demand', {
            actionName: 'toggle_page_option',
            params: [{name: 'header_hide'}],
        });
    },

    _setActive: function () {
        this._super.apply(this, arguments);
        var enabled;
        this.trigger_up('action_demand', {
            actionName: 'get_page_option',
            params: ['header_hide'],
            onSuccess: value => {
                this.$el.find('[data-hide]').toggleClass('active', !!value);
            },
        });
    },


});

options.registry.footerHide = options.Class.include({

    footerhide: function () {
        var self = this;
        this.trigger_up('action_demand', {
            actionName: 'toggle_page_option',
            params: [{name: 'footer_hide'}],
        });
    },

    _setActive: function () {
        this._super.apply(this, arguments);
        var enabled;
        this.trigger_up('action_demand', {
            actionName: 'get_page_option',
            params: ['footer_hide'],
            onSuccess: value => {
                this.$el.find('[data-footerhide]').toggleClass('active', !!value);
            },
        });
    },


});

});
