odoo.define('nav_side_menu_business.style', function (require) {
    "use strict";
    require('web.dom_ready');

    $("nav.navbar.navbar-default").insertBefore($("div#wrap"));

    $("#sidebar").mCustomScrollbar({
        theme: "minimal"
    });

    $('#dismiss, .overlay').on('click', function () {
        $('#sidebar').removeClass('active');
        $('.overlay').removeClass('active');
    });

    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').addClass('active');
        $('.overlay').addClass('active');
        $('.collapse.in').toggleClass('in');
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
    });
    $('#wrap').after($('footer.o_footer'));
    if($('.oe_website_login_container').length) {
        $('footer').hide();
        $('nav.navbar.navbar-default').hide();
    };
});
