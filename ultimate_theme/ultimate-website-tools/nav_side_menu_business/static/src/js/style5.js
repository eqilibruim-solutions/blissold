odoo.define('nav_side_menu_business.style', function (require) {
    "use strict";
    require('web.dom_ready');

    $("nav.navbar.navbar-default").insertBefore($("div#wrap"));


    $('#sidebarCollapse5').on('click', function () {
        $('#sidebar').toggleClass('active');
        $(this).toggleClass('active');
    });
    $('#wrap').after($('footer.o_footer'));
    if($('.oe_website_login_container').length) {
        $('footer').hide();
        $('nav.navbar.navbar-default').hide();
    };
});
