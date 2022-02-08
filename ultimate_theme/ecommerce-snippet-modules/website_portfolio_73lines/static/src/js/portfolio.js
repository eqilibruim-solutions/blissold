/*
    Part of Odoo Module Developed by 73lines
    See LICENSE file for full copyright and licensing details.
*/

//function portFilter(categ) {
//    var category = categ.trim();
//    $(document).find(".portfolio-list .portfolio-single").each(function(){
//        var port_categ = $(this).attr('category');
//        if (category == 'All') {
//            $(this).parent().fadeIn(1000);
//        } else {
//            if (port_categ.trim() == category) {
//                $(this).parent().fadeIn(1000);
//            } else {
//                $(this).parent().fadeOut(1000);
//            }
//        }
//    });
//}
$( document ).ready(function() {
  /* activate jquery isotope */
  var $container = $('#posts').isotope({
    itemSelector : '.item',
    isFitWidth: true
  });
  $container.isotope({ filter: '*' });

    // filter items on button click
  $('#filters').on( 'click', 'button', function() {
    var filterValue = $(this).attr('data-filter');
    $container.isotope({ filter: filterValue });
  });
});

