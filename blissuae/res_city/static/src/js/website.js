odoo.define('website_sale.advanced_wishlist_js', function(require) {
    "use strict";
    var ajax = require('web.ajax');
    // var core = require('web.core');
    // var _t = core._t;

    var publicWidget = require('web.public.widget');
    var wSaleUtils = require('website_sale.utils');
    var VariantMixin = require('sale.VariantMixin');


    publicWidget.registry.WebsiteAdvanvedWishlist = publicWidget.Widget.extend(VariantMixin, {
        selector: '.oe_website_sale',
        read_events: {
            'change select[name="state_id"]': '_onChangeState',
            'change input[name="pref_date"]': '_onChangePrefDate',
        },

        /**
         * @constructor
         */
        init: function () {
            this._super.apply(this, arguments);
            this._changeState = _.debounce(this._changeState.bind(this), 500);
        },
        /**
         * @override
         */
        start: function () {
            var self = this;
            var def = this._super.apply(this, arguments);
            this.$('select[name="state_id"]').change();
            return def;
        },

        /**
         * @private
         */
        _changeState: function () {
            if (!$('select[name="state_id"]').val()) {
                return;
            }
            this._rpc({
                route: "/shop/area_infos/" + $('select[name="state_id"]').val(),
            }).then(function (data) {
                // placeholder phone_code
                //$("input[name='phone']").attr('placeholder', data.phone_code !== 0 ? '+'+ data.phone_code : '');

                // populate states and display
                var selectAreas = $("select[name='city_id']");
                // dont reload state at first loading (done in qweb)
                console.log(data.areas.length)
                if (data.areas.length > 1) {
                    selectAreas.html('');
                    _.each(data.areas, function (x) {
                        var opt = $('<option>').text(x[1])
                            .attr('value', x[0]);
                        selectAreas.append(opt);
                    });
                    selectAreas.parent('div').show();

                } else {
                    selectAreas.val('').parent('div').hide();
                }
            });
        },
        _changePrefDate: function () {
            console.log($('input[name="pref_date"]').val())
            if (!$('input[name="pref_date"]').val()) {
                return;
            }
            this._rpc({
                route: "/shop/timeslots/" + $('input[name="pref_date"]').val(),
            }).then(function (data) {
                console.log(data.slots.length)
                var selectAreas = $("select[name='time_slot']");
                if (data.slots.length > 0){
                    var init = $('<option>').text("Select date for available slots").attr('value', '');
                }
                else{
                    var init = $('<option>').text("Slots unavailable, Please select another date").attr('value', '');

                }
                selectAreas.empty();
                selectAreas.append(init);
                // dont reload state at first loading (done in qweb)
                console.log((selectAreas.data('init')===0 || selectAreas.find('option').length===1))
                if (selectAreas.data('init')===0 || selectAreas.find('option').length===1) {
                    if (data.slots.length) {
                        selectAreas.empty();
                        _.each(data.slots, function (x) {
                            var opt = $('<option>').text(x[1])
                                .attr('value', x[0]);
                            selectAreas.append(opt);
                        });
                    }
                }
                selectAreas.data('init', 0);
            });
        },        
        _onChangePrefDate: function (ev) {
            this._changePrefDate();
        },
        _onChangeState: function (ev) {
            this._changeState();
        },
    });

    publicWidget.registry.WebsiteSale.include({


        _changeCountry: function () {
            console.log('Changing Countries')
            this._super.apply(this, arguments);
            console.log('Changes Applied')
            $('select[name="state_id"]').trigger('change');
        },

    });

});