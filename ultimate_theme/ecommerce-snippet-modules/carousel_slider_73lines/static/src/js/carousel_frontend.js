/*
    Part of Odoo Module Developed by 73lines
    See LICENSE file for full copyright and licensing details.
*/
odoo.define('carousel_slider_73lines.carousel_frontend', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var sAnimation = require('website.content.snippets.animation');

    sAnimation.registry.js_get_objects = sAnimation.Class.extend({
        selector: ".js_get_objects",
        disabledInEditableMode: false,

        start: function () {
            this.redraw();
        },

        destroy: function () {
           this.clean();
            this._super.apply(this, arguments);
        },

        redraw: function (debug) {
           this.clean(debug);
            this.build(debug);
        },

        clean: function () {
            this.$target.empty();
        },

        apply_carousel: function (debug) {
            var self = this;
            $(".owl-carousel").owlCarousel({
                loop: false,
                dots: false,
                nav: true,
                pagination: false,
                autoplay: false,
                margin: 20,
                navText: ["<i class='fa fa-long-arrow-left'></i>", "<i class='fa fa-long-arrow-right'></i>"],
                responsiveClass: true,
                responsive: {
                    768: {
                        items: 2
                    },
                    979: {
                        items: 2
                    },
                    479: {
                        items: 1
                    },
                    320: {
                        items: 1
                    },
                    1199: {
                        items: self.$target.data("objects_in_slide")
                    },
                },
            });
        },

        build: function (debug) {
            var self = this,
                limit = self.$target.data("objects_limit"),
                in_row = self.$target.data("objects_in_row"),
                filter_id = self.$target.data("filter_by_filter_id"),
                objects_in_slide = self.$target.data("objects_in_slide"),
                object_name = self.$target.data("object_name"),
                template = self.$target.data("template");

            self.$target.attr("contentEditable", false);

            if (!objects_in_slide) {
                objects_in_slide = 3;
            }
            if (!limit) {
                limit = 6;
            }
            if (!in_row) {
                in_row = 1;
            }
            var rpc_end_point = '/carousel_slider/render/' + object_name;
            ajax.jsonRpc(rpc_end_point, 'call', {
                'template': template,
                'filter_id': filter_id,
                'objects_in_slide': objects_in_slide,
                'limit': limit,
                'object_name': object_name,
                'in_row': in_row,
            }).then(function (objects) {
                $(objects).appendTo(self.$target);
                self.apply_carousel(objects);
            }).then(function () {
                self.loading(debug);
            });
//            .fail(function () {
//                return;
//            });
        },

        // function to hook things up after build
        loading: function (debug) {
        },


    });
});
