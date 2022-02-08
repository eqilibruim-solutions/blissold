odoo.define('website_sale_stock.ProductConfiguratorMixin', function (require) {
'use strict';

var ProductConfiguratorMixin = require('sale.ProductConfiguratorMixin');
var sAnimations = require('website.content.snippets.animation');
var ajax = require('web.ajax');
var core = require('web.core');
var QWeb = core.qweb;
var xml_load = ajax.loadXML(
    '/website_sale_stock/static/src/xml/website_sale_stock_product_availability.xml',
    QWeb
);

/**
 * Addition to the product_configurator_mixin._onChangeCombination
 *
 * This will prevent the user from selecting a quantity that is not available in the
 * stock for that product.
 *
 * It will also display various info/warning messages regarding the select product's stock.
 *
 * This behavior is only applied for the web shop (and not on the SO form)
 * and only for the main product.
 *
 * @param {MouseEvent} ev
 * @param {$.Element} $parent
 * @param {Array} combination
 */
ProductConfiguratorMixin._onChangeCombinationStock = function (ev, $parent, combination) {
    var product_id = 0;
    // needed for list view of variants
    if ($parent.find('input.product_id:checked').length) {
        product_id = $parent.find('input.product_id:checked').val();
    } else {
        product_id = $parent.find('.product_id').val();
    }
    var isMainProduct = combination.product_id &&
        ($parent.is('.js_main_product') || $parent.is('.main_product')) &&
        combination.product_id === parseInt(product_id);

    if (!this.isWebsite || !isMainProduct){
        return;
    }

    var qty = $parent.find('input[name="add_qty"]').val();
    
    var $add_button = $parent.find('#add_to_cart')
    var $qty_button = $parent.find('.js_add_cart_json');
    var $input_add_qty = $parent.find('input[name="add_qty"]');
    var $div_qty = $parent.find('.css_quantity')
    console.log($div_qty )
    console.log(combination.virtual_available)

    $add_button.removeClass('out_of_stock');
    $add_button.removeClass('d-none');
    $qty_button.removeClass('disabled');
    $div_qty.removeClass('d-none');

    if (combination.product_type === 'product' && _.contains(['always', 'threshold'], combination.inventory_availability)) {
        combination.virtual_available -= parseInt(combination.cart_qty);
        if (combination.virtual_available < 0) {
            combination.virtual_available = 0;
        }
        // Handle case when manually write in input
        if (qty > combination.virtual_available) {
            qty = combination.virtual_available || 1;
            $input_add_qty.val(qty);
        }
        if (combination.bom_ids.length == 0){
            if (qty > combination.virtual_available
                || combination.virtual_available < 1 || qty < 1) {
                $add_button.addClass('disabled out_of_stock d-none');
                $qty_button.addClass('disabled');
                $div_qty.addClass('d-none');
            }
        }
        else{
            if (qty > combination.immediately_usable_qty
                || combination.immediately_usable_qty < 1 || qty < 1) {
                $add_button.addClass('disabled out_of_stock d-none');
                $qty_button.addClass('disabled');
                $div_qty.addClass('d-none');

            }   
        }
    }
    xml_load.then(function () {
        $('.oe_website_sale')
            .find('.availability_message_' + combination.product_template)
            .remove();

        var $message = $(QWeb.render(
            'website_sale_stock.product_availability',
            combination
        ));
        $('div.availability_messages').html($message);
    });
};

sAnimations.registry.WebsiteSale.include({
    /**
     * Adds the stock checking to the regular _onChangeCombination method
     * @override
     */
    _onChangeCombination: function (){
        this._super.apply(this, arguments);
        ProductConfiguratorMixin._onChangeCombinationStock.apply(this, arguments);
    }
});

return ProductConfiguratorMixin;

});