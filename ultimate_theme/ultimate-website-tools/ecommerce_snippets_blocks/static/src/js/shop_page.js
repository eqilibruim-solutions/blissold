$(document).ready(function(){
      $('.oe_website_sale').each(function() {
            var oe_website_sale = this;

            var $attr_to_reorder = $('#products_grid_before > form.js_attributes', oe_website_sale);

            var $categ_to_reorder = $('#products_grid_before > ul#o_shop_collapse_category', oe_website_sale);

            var $heading_to_reorder = $('.category-heading',oe_website_sale);

            $categ_to_reorder.insertBefore($attr_to_reorder);

            $heading_to_reorder.insertBefore($categ_to_reorder);
        });

        /*---- Alternative Product ----*/
         $('.owl-carousel').owlCarousel({
            loop: true,
            autoplay: true,
            pagination: true,
            responsive: {
                0: {
                    items: 2,
                    nav: false
                },
                600: {
                    items: 4,
                    nav: false
                },
                1000: {
                    items: 4,
                    nav: true,
                }
            },
             navText : ["<i class='fa fa-chevron-left'></i>","<i class='fa fa-chevron-right'></i>"]
        });
});
