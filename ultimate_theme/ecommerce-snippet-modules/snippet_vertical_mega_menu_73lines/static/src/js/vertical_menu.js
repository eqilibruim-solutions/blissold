/*
    Part of Odoo Module Developed by 73lines
    See LICENSE file for full copyright and licensing details.
*/

$(function () {
    // init bootstrap collapse for elements with sub-categ-page class
    $('.sub-categ-page').collapse({toggle: false});

    $('body').on('click', '[data-toggle=collapse-next]', function (e) {
        // Try to close all of the collapse areas first
        var parent_id = $(this).data('parent');
        $(parent_id+' .sub-categ-page').collapse('hide');

        // ...then open just the one we want
        var $target = $(this).parents('.panel').find('.sub-categ-page');
        $target.collapse('toggle');
    });

    $('body').on('click', function (e) {
        // Try to close all of the collapse areas when click anywhere in body, if not in edit mode
        if ($('body.editor_enable').length == 0) {
            $('.sub-categ-page').collapse('hide');
        }
    });
});

odoo.define('snippet_vertical_mega_menu_73lines.editor', function (require) {
    'use strict';
    var options = require('web_editor.snippets.options');

    options.registry.vertical_category_menu = options.Class.extend({
//        selector: ".vertical_category_menu",

        start : function () {
            var self = this;
            this._super();
            this.$indicators = this.$target.find('#category_menu');
        },

        add_category: function(type, data) {
            console.log("typeeeeeeeeeeeeeee",type);
            console.log("dataaaaaaaaaaaaaa",data);
            var ul = document.getElementById("category_menu"),
                li = document.createElement("li"),
                alink = document.createElement("a"),
                children = this.$indicators.children().length + 1,
                li_id = "categ_"+children,
                alink_id = "categ_link_"+children;
            li.setAttribute("id", li_id);
            alink.setAttribute("id", alink_id);
            alink.setAttribute("class", 'o_default_snippet_text');
            li.appendChild(document.createTextNode("Category Menu"));

            this.$indicators.append(li);
            this.$target.find( "#"+li_id ).wrapInner( alink );
        },

        add_sub_page: function(type, data) {
            console.log("aaaaaaa targettttttt",this.$target);
            this.$target.replaceWith(
                "<li class='panel'>" +
                    "<a class='accordion-toggle' data-toggle='collapse-next' data-target='#category_menu'>" +
                        "<span class='fa fa-caret-right'/> Category Menu" +
                    "</a>" +
                    "<ul class='collapse sub-categ-page'>" +
                        "<div id='wrap' class='sub_category_page'>" +
                            "<div class='oe_structure container'>" +
                            "</div>" +
                        "</div>" +
                    "</ul>" +
                "</li>"
            );
            $(".oe_active").removeClass("oe_active");
        },

    });

});
