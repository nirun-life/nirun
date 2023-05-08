/** @odoo-module */

import {FormLabel} from "@web/views/form/form_label";
import {patch} from "web.utils";

patch(FormLabel.prototype, "web_form_label_asterisk.isRequired", {
    get isRequired() {
        const field = this.props.record.fields[this.props.fieldName];
        return field.required;
    },
});
