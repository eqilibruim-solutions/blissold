odoo.define('google_dynamic_font.theme', function (require) {
    'use strict';

    var Theme = require('website.theme');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var Dialog = require('web.Dialog');

    var qweb = core.qweb;
    var _t = core._t;

    ajax.loadXML('/google_dynamic_font/static/src/xml/base.xml', core.qweb);
    Theme.include({
        events: _.extend({}, Theme.prototype.events, {
            'click .add-font': '_addFont',
            'click .remove-font': '_removeFont',
            'mouseover .align-items-center': '_setTooltip',
        }),
        init: function (parent, options) {
            this.gf_url = 'https://fonts.googleapis.com/css?family=';
            this._super.apply(this, arguments);
        },
        _generateDialogHTML: function(){
            this._super.apply(this, arguments);
            var $tab = this.$el.find('[class*="o_theme_customize_option_font_"]').closest('.tab-pane');
            var html = qweb.render('FontCustomizer', {});
            $tab.prepend(html)
        },
        _addFont: function (e) {
            e.preventDefault();
            var self = this;
            var url = this.$el.find('.txt_url').val();
            if (url.indexOf(this.gf_url) >= 0) {
                ajax.jsonRpc('/web/add_google_font', 'call', {url: url})
                    .then(function (data) {
                        if(data.error){
                            self._errGoogleFontURL(data.error);
                        } else {
                            window.location.hash = 'theme=true&tab=' +  self.$el.find('.tab-pane.active.show').index();
                            window.location.reload();
                        }
                    });
            } else {
                var msg = "Please Enter Valid Google Font URL."
                self._errGoogleFontURL(msg);
            }
        },
        _removeFont: function (e) {
            e.preventDefault();
            var self = this;
            new Dialog(this, {
                size: 'medium',
                title: _t("Delete"),
                $content: $("<h5>Are you sure you want to Delete?</h5>"),
                buttons: [{
                    text: 'Delete',
                    classes : "btn-danger",
                    click: function () {
                        var xmlid = $(e.currentTarget).data('xmlid');
                        ajax.jsonRpc('/web/remove_google_font', 'call', {xmlid: xmlid})
                            .then(function (data) {
                                window.location.hash = 'theme=true&tab=' +  self.$el.find('.tab-pane.active.show').index();
                                window.location.reload();
                            });
                    },
                    close:true,
                }, {
                    text: _t("Cancel"),
                    close: true,
                }],
            }).open();
        },
        _setActive: function () {
            this._super.apply(this, arguments);
            this.$el.find('[class*="o_theme_customize_option_font"] .remove-font[data-xmlid]').show();
            var $enable = this.$inputs.filter('[data-xmlid]:checked').not('.remove-font');
            _.each($enable, function (input) {
                input = $(input);
                input.parents('.o_theme_customize_option').find('.remove-font').hide();
            });
        },
        _errGoogleFontURL: function (msg) {
            new Dialog(this, {
                size: 'medium',
                title: _t("Error"),
                $content: $("<h5>"+ msg + "</h5>"),
                buttons: [{
                    text: _t("Cancel"),
                    close: true,
                }],
            }).open();
        },
        _setTooltip: function(e){
            var span_val = $(e.target).find('span')[0];
            if(span_val){
                if($(e.target)[0].nodeName == 'SPAN'){
                    var span_text = $(e.target)[0];
                    var str_span = window.getComputedStyle(span_text, ':before').getPropertyValue('content');
                    var result = str_span.substring(1, str_span.length-1);
                    $(e.target).parent().attr('title',result)

                }
            }
        }
    });

});