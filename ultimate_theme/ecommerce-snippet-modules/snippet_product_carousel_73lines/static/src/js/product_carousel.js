/*
    Part of Odoo Module Developed by 73lines
    See LICENSE file for full copyright and licensing details.
*/

window.setInterval(function(){
    if ($('li.add_to_cart_js').length && $('li.price_js').hasClass('active')) {
        $('li.add_to_cart_js').addClass('hidden');
    } else {
        $('li.add_to_cart_js').removeClass('hidden');
    }
}, 1000);
odoo.define('product_carousel_73lines.carousel_frontend', function(require) {
    "use strict";
    var website_sale_utils = require('website_sale.utils');
    var sAnimation = require('website.content.snippets.animation');
    var ajax = require('web.ajax');

    sAnimation.registry.js_get_objects.include({
        events: {
        'click .o_add_wishlist':'wishlistClick',
        },
        init: function(){
            this._super.apply(this, arguments);
            this.wishlist_product_ids = [];
        },
        wishlistClick: function(e){
            var self = this;
            $.get('/shop/wishlist', {'count': 1}).then(function(res) {
                self.wishlist_product_ids = JSON.parse(res);
            });
            this.add_new_products($(e.target).parent(), e);
        },
        add_new_products:function($el, e){
            var self = this;
            var product_id = typeof($(e.target).data('product-product-id')) === 'undefined' ? $el.data('product-product-id') : $(e.target).data('product-product-id');
            if (e.currentTarget.classList.contains('o_add_wishlist_dyn')) {
                product_id = parseInt($el.parent().find('.product_id').val());
            }
            if (!_.contains(self.wishlist_product_ids, product_id)) {
                return ajax.jsonRpc('/shop/wishlist/add', 'call', {
                    'product_id': product_id
                }).then(function () {
                    self.wishlist_product_ids.push(product_id);
                    website_sale_utils.animate_clone($('#my_wish'), $el.closest('form'), 25, 40);
                    $el.prop("disabled", true).addClass('disabled');
                    $('#my_wish').show();
                    $('.my_wish_quantity').text(self.wishlist_product_ids.length);
                });
            }
        },
    });
});
