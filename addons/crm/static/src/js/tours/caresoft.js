odoo.define('example.tour', function(require) {
"use strict";

var core = require('web.core');
var tour = require('web_tour.tour');

var _t = core._t;

tour.register('example_tour', {
    url: "/web",
}, [tour.STEPS.MENU_MORE, {
    trigger: '.o_app[data-menu-xmlid="contacts.menu_contacts"]',
    content: _t('Want to <b>create customers</b>?<br/><i>Click on Contacts to start.</i>'),
    position: 'bottom',
}
}]);

});