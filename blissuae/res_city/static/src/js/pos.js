odoo.define('res_city.partner', function (require) {
"use strict";

var models = require('point_of_sale.models');
var core = require('web.core');
var screens = require('point_of_sale.screens');
var gui = require('point_of_sale.gui');

var QWeb = core.qweb;


models.load_models([{
    model:  'res.city',
    fields: [],
    loaded: function(self,city_ids){
        self.city_ids = city_ids;
    },
}]);



models.load_fields("res.partner", "city_id");
models.load_fields("res.partner", "mobile");

});