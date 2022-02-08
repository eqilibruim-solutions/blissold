odoo.define('content.inherit', function (require) {
    'use strict';

var ContentMenu = require("website.contentMenu")
var core = require('web.core');
var wUtils = require('website.utils');

var _t = core._t;

ContentMenu.ContentMenu.include({

    pageOptionsSetValueCallbacks: {
        header_overlay: function (value) {
            $('#wrapwrap').toggleClass('o_header_overlay', value);
        },
        header_color: function (value) {
            $('#wrapwrap > header').removeClass(this.value)
                                   .addClass(value);
        },
        header_hide: function (value) {
            $('#wrapwrap').toggleClass('o_header_hide', value);
        },
        footer_hide: function (value) {
            $('#wrapwrap').toggleClass('o_footer_hide', value);
        }
    },




});


});
