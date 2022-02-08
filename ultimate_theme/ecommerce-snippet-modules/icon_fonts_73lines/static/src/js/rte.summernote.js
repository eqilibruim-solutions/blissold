/*
    Part of Odoo Module Developed by 73lines
    See LICENSE file for full copyright and licensing details.
*/
odoo.define('icon_fonts_73lines.rte.summernote', function (require) {
    'use strict';

    var widgets = require('icon_fonts_73lines.widgets');
    var core = require('web.core');
    require('web_editor.rte.summernote');

    var _t = core._t;

    var eventHandler = $.summernote.eventHandler;
    var renderer = $.summernote.renderer;

    var tplIconButton = renderer.getTemplate().iconButton;
    var tplButton = renderer.getTemplate().button;

    var fn_attach = eventHandler.attach;
    eventHandler.attach = function (oLayoutInfo, options) {
        fn_attach.call(this, oLayoutInfo, options);

        create_icon_feature("div.open-icons-dialog button", function () {
            new widgets.FontIconDialog().open();
        });

        function create_icon_feature(selector, callback) {
            oLayoutInfo.popover().on("click", selector, function (e) {
                if ($(e.target).closest(".note-toolbar").length) return; // prevent icon edition of top bar for default summernote
                callback();
            });
        }

    };

    var fn_tplPopovers = renderer.tplPopovers;
    renderer.tplPopovers = function (lang, options) {
        var $popover = $(fn_tplPopovers.call(this, lang, options));
        var $imagePopover = $popover.find('.note-image-popover');

        var $icons = $('<div class="btn-group hidden only_fa open-icons-dialog"/>').insertAfter(
            $imagePopover.find('.btn-group:has([data-event="resize"])'));
        $(tplIconButton('fa fa-gears', {
            title: _t('Icons'),
        })).appendTo($icons);

        return $popover;
    };

});
