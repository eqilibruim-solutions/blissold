/*
    Part of Odoo Module Developed by 73lines
    See LICENSE file for full copyright and licensing details.
*/
odoo.define('carousel_slider_73lines.carousel_editor', function (require) {
    "use strict";

    var core = require('web.core');
    var sAnimation = require('website.content.snippets.animation');
    var options = require('web_editor.snippets.options');
    var rpc = require('web.rpc');

    var _t = core._t;


    options.registry.js_get_objects = options.Class.extend({
        onBuilt: function () {
            var self = this;
            this._super.apply(this, arguments);
            if (!self.$target.data('snippet-view')) {
                this.$target.data("snippet-view", new sAnimation.registry.js_get_objects(this.$target));
            }
        },

        cleanForSave: function () {
            this._super.apply(this, arguments);
            this.$target.empty();
        },
    });

    options.registry.js_get_objects_in_row = options.Class.extend({
        start: function () {
            var self = this;
            setTimeout(function () {
                var wecollapse =self.$el.find(".snippet-option-js_get_objects_in_row > .row_div");
                if (self.$target.attr("data-objects_in_row")) {
                    var in_row = self.$target.attr("data-objects_in_row");
                    wecollapse.find('we-button[data-objects_in_row="' + in_row + '"]').addClass("active");
                } else {
                    wecollapse.find('we-button[data-objects_in_row="1"]').addClass("active");
                }
            }, 100)
        },

        objects_in_row: function (type, value, $webutton) {
            var self = this;
            if (type != false) {
                return
            }
            value = parseInt(value);
            this.$target.attr("data-objects_in_row", value).data("objects_in_row", value)
            self.trigger_up('widgets_start_request', {
                    editableMode: true,
                    $target: this.$target,
            });
            setTimeout(function () {
                $webutton.parent().find("we-button").removeClass("active");
                $webutton.addClass("active");
            }, 100);
        },
    });

    options.registry.js_get_objects_limit = options.Class.extend({
        start: function () {
            var self = this;
            setTimeout(function () {
                var wecollapse = self.$el.find(".snippet-option-js_get_objects_limit");
                if (self.$target.attr("data-objects_limit")) {
                    var limit = self.$target.attr("data-objects_limit");
                    wecollapse.find('we-button[data-objects_limit="' + limit + '"]').addClass("active");
                } else {
                    wecollapse.find('we-button[data-objects_limit="6"]').addClass("active");
                }
            }, 100)
        },

        objects_limit: function (type, value, $webutton) {
            var self = this;
            if (type != false) {
                return
            }
            value = parseInt(value);
            this.$target.attr("data-objects_limit", value).data("objects_limit", value);
            self.trigger_up('widgets_start_request', {
                    editableMode: true,
                    $target: this.$target,
            });
            setTimeout(function () {
                $webutton.parent().find("we-button").removeClass("active");
                $webutton.addClass("active");
            }, 100);
        }

    });

    options.registry.js_get_objects_in_slide = options.Class.extend({
        start: function () {
            var self = this;
            setTimeout(function () {
                var wecollapse = self.$el.find(".snippet-option-js_get_objects_in_slide > .slides_div");
                if (self.$target.attr("data-objects_in_slide")) {
                    var prd_limit = self.$target.attr("data-objects_in_slide");
                    wecollapse.find('we-button[data-objects_in_slide="' + prd_limit + '"]').addClass("active");
                } else {
                    wecollapse.find('we-button[data-objects_in_slide="3"]').addClass("active");
                }
            }, 100)
        },

        objects_in_slide: function (type, value, $webutton) {
            var self = this;
            if (type != false) {
                return
            }
            value = parseInt(value);
            this.$target.attr("data-objects_in_slide", value).data("objects_in_slide", value);
            self.trigger_up('widgets_start_request', {
                editableMode: true,
                $target: self.$target,
            });
            setTimeout(function () {
                $webutton.parent().find("we-button").removeClass("active");
                $webutton.addClass("active");
            }, 100);
        }
    });

    options.registry.js_get_objects_selectFilter = options.Class.extend({
          init: function () {
                this._super.apply(this, arguments);
            },

        start: function () {
            this._super();
            var self = this;
            rpc.query({
                model: 'ir.filters',
                method: 'search_read',
                domain: [['context', 'not like', 'group_by'], ['model_id', '=', self.$target.attr("data-object_name")]],
                fields: ['name', 'id'],
            }).then(function (filters) {
                self.createfiltersList(filters)
            });
//            .fail(function (e) {
//                var title = _t("Oops, Huston we have a problem"),
//                    msg = $("<div contenteditable='false' class='message error text-center'><h3>" + title + "</h3><code>" + e.data.message + "</code></div>");
//                self.$target.append(msg)
//                return;
//            });
        },

        createfiltersList: function (filters) {
            var self = this;
            var wecollapse = null;
            setTimeout(function () {
//                ul = self.$overlay.find(".snippet-option-js_get_objects_selectFilter > div");
//                ul = self.$overlay.find(".snippet-option-js_get_objects_selectFilter").find('>div').find('>div');
//                if (self.$overlay.hasClass('.oe_active'))
//                {
//                    wecollapse = self.$el.find("we-collapse-area.snippet-option-js_get_objects_selectFilter > .filter_div");
//                }
//                else{
//                    wecollapse = ('.filter_div')
//                }
                 wecollapse = self.$el.find("we-collapse-area.snippet-option-js_get_objects_selectFilter > .filter_div");
                $(filters).each(function () {
                    var filter = $(this);
//                    var li = $('<li class="dropdown-item" data-filter_by_filter_id="' + filter[0].id + '"><a>' + filter[0].name + '</a></li>');
                    var webutton = $('<we-button data-filter_by_filter_id="' + filter[0].id + '">' + filter[0].name + '</we-button>');
                    wecollapse.append(webutton);
                });
                if (self.$target.attr("data-filter_by_filter_id")) {
                    var id = self.$target.attr("data-filter_by_filter_id");
                    wecollapse.find("we-button[data-filter_by_filter_id=" + id + "]").addClass("active");
                } else {
                    wecollapse.find('we-button[data-filter_by_filter_id=""]').addClass("active");

                }
            }, 100)
        },

        filter_by_filter_id: function (type, value, $webutton,) {
            var self = this;
            if (type == false) {
                $webutton.parent().find("we-button").removeClass("active");
                $webutton.addClass("active");
                value = parseInt(value);
                self.$target.attr("data-filter_by_filter_id", value).data("filter_by_filter_id", value).data('snippet-view');
                self.trigger_up('widgets_start_request', {
                    editableMode: true,
                    $target: this.$target,
                });
            }
        }
    });
});
