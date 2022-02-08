odoo.define('website_sale_checkout_extra_fields.validate_fields', function (require) {
    "use strict"

    $(document).ready(function() {

        $(".o_website_form_date").datepicker({ 
                                               minDate: $(".o_website_form_date").data('min'),
                                               dateFormat: "dd/mm/yy"
                                           });
        if ($("#delivery_note") && $("#delivery_note").length > 0) {
                $('#delivery_note').val($('#delivery_note').data("value"));
            };
        if ($("#gift_message") && $("#gift_message").length > 0) {
                $('#gift_message').val($('#gift_message').data("value"));
            };

        });



    require('web.dom_ready')
    let ajax = require('web.ajax')
    let $checkout_link = $('a[href*="/shop/checkout"]')
    let $inputs = $('.js_wscef_field')
    if($checkout_link.length && $inputs.length) {
        $checkout_link.on('click',function(e){
            e.preventDefault()
            var values = {};
            $inputs.each(function(index){
                values[($(this).attr('name'))] = $(this).val()
            })
            ajax.jsonRpc('/shop/cart/validation', 'call', {
                'values': values,
            }).then(function (result) {
                if (result['error'].length == 0){
                    window.location = $checkout_link.attr('href')
                } else {
                    $('.js_wscei_errors').removeClass('d-none')
                    let $errors = $('.js_wscei_errors ul')
                    let $errors_items = $('.js_wscei_errors ul li')
                    $errors_items.remove()
                    for (var i = 0; i < result['error'].length; i++) {
                        $errors.append('<li class="list-item">' + result['error'][i] + '</li>').append($errors)
                    }
                }
            })
        })
    }
})
