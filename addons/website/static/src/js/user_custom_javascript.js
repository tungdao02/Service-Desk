//
// This file is meant to regroup your javascript code. You can either copy/past
// any code that should be executed on each page loading or write your own
// taking advantage of the Odoo framework to create new behaviors or modify
// existing ones. For example, doing this will greet any visitor with a 'Hello,
// world !' message in a popup:
//
/*
odoo.define('website.user_custom_code', function (require) {
'use strict';

var Dialog = require('web.Dialog');
var publicWidget = require('web.public.widget');

publicWidget.registry.HelloWorldPopup = publicWidget.Widget.extend({
    selector: '#wrapwrap',

    start: function () {
        Dialog.alert(this, "Hello, world!");
        return this._super.apply(this, arguments);
    },
})
});
*/


odoo.define('website.user_custom_code', function (require) {
    'use strict';
    
    var Dialog = require('web.Dialog');
    var publicWidget = require('web.public.widget');
    
    publicWidget.registry.HelloWorldPopup = publicWidget.Widget.extend({
        selector: '#wrapwrap',
    
        start: function () {
            
            if(document.getElementById("mother_category") != null && document.getElementById("category") != null){
    
    
                var a = document.getElementById("mother_category");
                var b = document.getElementById("category");
    
    
    
                b.value = "0"
                let mother_category_text = "";
                for(let i=0 ; i< a.length; i++){
                    if(a[i].value == a.value){
                        mother_category_text = a[i].innerText.trim();
                    }
                }
                
                
                for(let i=0 ; i<b.length ; i++){
                    console.log(b[i].getAttribute("class"))
                }
                
                
                for(let i = 0 ; i < b.length; i++){
                    if(b[i].getAttribute("class") == mother_category_text){
                        
                        b[i].style.display = "inline";
                        console.log(b[i]);
                    }else {
                        b[i].style.display = "none";
                         console.log(b[i]);
                        
                    }
                    
                }
                
                
                
                
                
                a.addEventListener("change", function() {   
                b.value = "0"
                let mother_category_text = "";
                for(let i=0 ; i< a.length; i++){
                    if(a[i].value == a.value){
                        mother_category_text = a[i].innerText.trim();
                    }
                }
                
                
                for(let i=0 ; i<b.length ; i++){
                    console.log(b[i].getAttribute("class"))
                }
                
                
                for(let i = 0 ; i < b.length; i++){
                    if(b[i].getAttribute("class") == mother_category_text){
                        
                        b[i].style.display = "inline";
                        console.log(b[i]);
                    }else {
                        b[i].style.display = "none";
                         console.log(b[i]);
                        
                    }
                    
                }
                
                });
                
                }
            
    
    
            return this._super.apply(this, arguments);
        },
    })
    });
    