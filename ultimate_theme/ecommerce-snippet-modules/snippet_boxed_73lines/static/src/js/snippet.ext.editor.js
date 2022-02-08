odoo.define('snippet_boxed_73lines.ext.editor', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');

    ajax.loadXML('/snippet_boxed_73lines/static/src/xml/s_media_block_modal_ext.xml', core.qweb);
});
