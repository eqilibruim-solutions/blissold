/*
    Part of Odoo Module Developed by 73lines
    See LICENSE file for full copyright and licensing details.
*/

odoo.define('website_stock_notify_73lines.stock_notify', function(require) {
    "use strict";

    var website_sale = require('website_sale.website_sale');

    $('.oe_website_sale').each(function () {
        var oe_website_sale = this;

        $(oe_website_sale).find('.js_product').ready(function(){
            var variant_ids = $('ul.js_add_cart_variants').data('attribute_value_ids');
            var values = [];
            $('ul.js_add_cart_variants').closest('.js_product').find('input.js_variant_change:checked, select.js_variant_change').each(function () {
                values.push(+$(this).val());
            });

            var product_available_qty = false;

            for (var k in variant_ids) {
                if (_.isEmpty(_.difference(variant_ids[k][1], values))) {
                    product_available_qty = variant_ids[k][4]
                    break;
                }
            }
            if (product_available_qty == 0) {
                $(oe_website_sale).find('#out_of_stock_product').removeClass('hidden');
                $(oe_website_sale).find('#add_to_cart').addClass('hidden');
                $(oe_website_sale).find('#message').addClass('hidden');
            } else {
                $(oe_website_sale).find('#out_of_stock_product').addClass('hidden');
                $(oe_website_sale).find('#add_to_cart').removeClass('hidden');
            }

        });

        $(oe_website_sale).on('change', 'input.js_product_change', function () {
            var product_available_qty = $(this).attr('qty_available');
            if (!product_available_qty || product_available_qty == 0.0) {
                $(oe_website_sale).find('#out_of_stock_product').removeClass('hidden');
                $(oe_website_sale).find('#add_to_cart').addClass('hidden');
                $(oe_website_sale).find('#message').addClass('hidden');
            } else {
                $(oe_website_sale).find('#out_of_stock_product').addClass('hidden');
                $(oe_website_sale).find('#add_to_cart').removeClass('hidden');
            }
        });

        $(oe_website_sale).on('change', 'input.js_variant_change, select.js_variant_change, ul[data-attribute_value_ids]', function (ev) {
            var $ul = $(ev.target).closest('.js_add_cart_variants');
            var $parent = $ul.closest('.js_product');
            var variant_ids = $ul.data("attribute_value_ids");
            var values = [];
            $parent.find('input.js_variant_change:checked, select.js_variant_change').each(function () {
                values.push(+$(this).val());
            });

            var product_available_qty = false;
            for (var k in variant_ids) {
                if (_.isEmpty(_.difference(variant_ids[k][1], values))) {
                    product_available_qty = variant_ids[k][4]
                    break;
                }
            }
            if (product_available_qty == 0) {
                $(oe_website_sale).find('#out_of_stock_product').removeClass('hidden');
                $(oe_website_sale).find('#add_to_cart').addClass('hidden');
                $(oe_website_sale).find('#message').addClass('hidden');
            } else {
                $(oe_website_sale).find('#out_of_stock_product').addClass('hidden');
                $(oe_website_sale).find('#add_to_cart').removeClass('hidden');
            }

        });

        $('div.js_product', oe_website_sale).each(function () {
            $('input.js_product_change', this).first().trigger('change');
        });

        $('.js_add_cart_variants', oe_website_sale).each(function () {
            $('input.js_variant_change, select.js_variant_change', this).first().trigger('change');
        });

        $(oe_website_sale).on('click', '#notify_submit', function(){
            var prod_id = $(oe_website_sale).find('.js_add_cart_variants .js_product .product_id').attr('value');
            $(oe_website_sale).find('#notify-form div #out_stock_product_id').attr('value', prod_id);

            $(oe_website_sale).on('submit', '#notify-form', function(e){
                $(oe_website_sale).find('#message').removeClass('hidden');
                $(oe_website_sale).find('#enter_email').addClass('hidden');
            });
        });

        $(oe_website_sale).on("change", ".oe_cart input.js_quantity[data-product-id]", function (ev) {
            var available_qty_cart_line = $(ev.target).closest('input.js_quantity.form-control').attr('available_qty');
            var added_qty_cart_line = $(ev.target).closest('input.js_quantity.form-control').attr('value');
            if (added_qty_cart_line > available_qty_cart_line) {
                $(ev.target).parent().next('div.out_of_stock').removeClass('hidden');
            }
        });

    });

    // Shopping Cart Line Condition
    $(document).ready(function () {
        if($('.oe_cart input.js_quantity').length) {
            setInterval(function(){
                for (var i = 0; i < $('.oe_cart input.js_quantity.form-control[data-product-id]').length; i++) {
                    var available_quantity = $('.oe_cart input.js_quantity.form-control[data-product-id]')[i].getAttribute('available_qty');
                    var value = $('.oe_cart input.js_quantity.form-control[data-product-id]')[i].value;
                    var product_id = $('.oe_cart input.js_quantity.form-control[data-product-id]')[i].getAttribute('data-product-id');
                    var product_id_check = $('.out_of_stock')[i].getAttribute('data-product-id');

                    if ((value > available_quantity) && (product_id == product_id_check)) {
                        $('.out_of_stock')[i].classList.remove('hidden');
                    } else {
                        $('.out_of_stock')[i].classList.add('hidden');
                    }
                }
                if ($('div.out_of_stock:not(.hidden)').length) {
                    $('a[href^="/shop/checkout"]').attr('disabled', 'disabled').css('pointer-events', 'none');
                } else {
                    $('a[href^="/shop/checkout"]').removeAttr('disabled', 'disabled');
                    $('a[href^="/shop/checkout"]').removeAttr('style');
                }
            }, 500);
        }
    });
});
