odoo.define('web_gantt_view.GanttController', function (require) {
"use strict";

var AbstractController = require('web.AbstractController');
var core = require('web.core');
var QWeb = core.qweb;
var Dialog = require('web.Dialog');
var dialogs = require('web.view_dialogs');
var time = require('web.time');

return AbstractController.extend({
    
    custom_events: _.extend({}, AbstractController.prototype.custom_events, {
        updateRecord: '_onUpdateRecord',
        openRecord: '_openRecord',
    }),

    renderButtons: function ($node) {
        this.$buttons = $(QWeb.render("GanttViewCreateButton", {widget: this}));
        this.$buttons.on('click', '.acs_gantt_button_create', this._createaRecord.bind(this));
        this.$buttons.appendTo($node);
    },

    _onUpdateRecord: function (record) {
        this._rpc({
            model: this.model.modelName,
            method: 'write',
            args: [record.data.id, {
                [this.model.data.arch['date_start']]: record.data[this.model.data.arch['date_start']],
                [this.model.data.arch['date_stop']]: record.data[this.model.data.arch['date_stop']],
            }],
        }).then(this.reload.bind(this));
    },

    _openRecord: function (record) {
        new dialogs.FormViewDialog(this, {
            res_model: this.model.modelName,
            res_id: record.data.id,
            on_saved: this.reload.bind(this)
        }).open();
    },

    _createaRecord: function () {
        new dialogs.FormViewDialog(this, {
            res_model: this.model.modelName,
            on_saved: this.reload.bind(this)
        }).open();
    },

});

});
