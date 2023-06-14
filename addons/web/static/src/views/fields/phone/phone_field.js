/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _lt } from "@web/core/l10n/translation";
import { useInputField } from "../input_field_hook";
import { standardFieldProps } from "../standard_field_props";
import { Component } from "@odoo/owl";

export class PhoneField extends Component {

    setup() {
        console.log(this.props.record.data.id);
        useInputField({ getValue: () => this.props.value || "" });
    }
    async call_out(ev) {
       var rpc = require('web.rpc');
       var result = await rpc.query({
            model: 'crm.lead',
            method: 'get_phone_info',
            args: [{
                value:'1'
            }]});
        if(result != null)
        {
            this.phone_initialize(this.call_end, this.save_call, this.props.record.data.id, result.domain, result.sip_user, result.password);
            await new Promise(resolve => setTimeout(resolve, 1500));
            document.querySelector('[role="dialog"]')?.remove();
            omiSDK.makeCall(this.props.value);
        }
        else
        {
            alert('User has not been provided a phone number. Contact admin for more information');
        }
    }
    phone_initialize(endCallback, saveCallback, lead_id, domain, sip_user, password)
        {
            var _lead_id = 0;
            var _initialized = 0;
            if(_initialized == 0)
            {
                _lead_id = lead_id;
                var config={theme:"default",debug:!0,busy:!1,language:"vi",ringtoneVolume:1.0,options:{showNoteInput:!1,hideCallButton:!1,showContactLoading:!1},styles:{dialog:{"background-color":"#c3bfbf",justifyContent:"center",color:"red"}},forms:[{id:"note1",label:"Ghi chú 1",plh:"Nhập ghi chú 1",className:"demo-custom-form form-note"},{id:"address",label:"Địa chỉ",plh:"Nhập ghi địa chỉ"},{id:"level",type:"multiselect",label:"Địa chỉ",selections:['Level 1','Level 2','Level 3','Level 4','Level 5','Level 6','Level 7']}],callbacks:{register:e=>{},connecting:e=>{},invite:e=>{},inviteRejected:e=>{},ringing:e=>{},accepted:e=>{},incall:e=>{},acceptedByOther:e=>{},ended:e=>{endCallback(e, _lead_id)},holdChanged:e=>{},saveCallInfo:e=>{saveCallback(e)}},ringtone_volume:1.0,form_ui:{call_button:{enabled:!1}},register_fn:e=>{console.log("[LEGACY_API] register_fn:",e)},incall_fn:e=>{console.log("[LEGACY_API] incall_fn:",e)},accept_fn:e=>{console.log("[LEGACY_API] accept_fn:",e)},endcall_fn:e=>{console.log("[LEGACY_API] endcall_fn:",e)},invite_fn:e=>{console.log("[LEGACY_API] invite_fn:",e)},invite_2fn:e=>{console.log("[LEGACY_API] invite_2fn:",e)},accept_out_fn:e=>{console.log("[LEGACY_API] accept_out_fn:",e)},ping_fn:e=>{console.log("[LEGACY_API] ping_fn:",e)}};
                omiSDK.init(config, () => {
                    let extension = {
                        domain: domain,
                        username: sip_user,
                        password: password,
                    };
                    omiSDK.register(extension);
                });
            }
            return true;
        }
    async save_call(data){
        var rpc = require('web.rpc');
        await rpc.query({
                    model: 'crm.lead',
                    method: 'call_note_end_handler',
                    args: [{
                        data
                    }]});
        rpc.query({
                    model: 'res.users',
                    method: 'view_lead_assigned',
                    args: [{data}]});
    }

    async call_end(data,lead_id){
        data['lead_id'] = lead_id;

        var rpc = require('web.rpc');
        await rpc.query({
                    model: 'crm.lead',
                    method: 'call_end_handler',
                    args: [{
                        data
                    }]});
        console.log(data);
    }
}

PhoneField.template = "web.PhoneField";
PhoneField.props = {
    ...standardFieldProps,
    placeholder: { type: String, optional: true },
};

PhoneField.displayName = _lt("Phone");
PhoneField.supportedTypes = ["char"];

PhoneField.extractProps = ({ attrs }) => {
    return {
        placeholder: attrs.placeholder,
    };
};

class FormPhoneField extends PhoneField {}
FormPhoneField.template = "web.FormPhoneField";


registry.category("fields").add("phone", PhoneField);
registry.category("fields").add("form.phone", FormPhoneField);
