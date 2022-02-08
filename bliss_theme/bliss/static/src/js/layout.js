odoo.define('bliss.website_layout', function (require) {
'use strict';


   require("web.dom_ready");

   $("#enterbliss_btn").click(function (ev) {
        $("#coverdiv").toggle('show')

   })


   $("#enterbliss_btn").click(function (ev) {
        $("#coverdiv").fadeOut()

   })
   $("input[name='is_delivry']").change(function(){
        $("#shipping_address_delivry").toggle('show')
        $("#shipping_address_pick_up").toggle('show')
   });
    $("input[name='is_card_credit']").change(function(ev){
        $("#credit-card-info").toggle('show')
   });
    $("input[name='user_shipping_address']").change(function(ev){
        $("#shippment_adress_from_payment").toggle('show')
   });
    $(".my_bag_edit_item").click(function(ev){
        $(this).parents("td").find("#product-qty").toggle('show')
   });


$( "#date_delivry" ).datepicker({changeMonth: true,changeYear: true,dateFormat: "dd/mm/yy"});




});
