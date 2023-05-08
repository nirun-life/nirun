/** @odoo-module **/

import {areDateEquals, formatDateTime} from "@web/core/l10n/dates";
import {DateTimeField} from "@web/views/fields/datetime/datetime_field";
import {patch} from "web.utils";

patch(DateTimeField.prototype, "l10n_th_web_buddhist_calendar.datetime_field", {
    get formattedValue() {
        let date = this.props.value;
        if (date.locale === "th-TH") {
            date = date.plus({year: 543});
        }
        return formatDateTime(date);
    },
    onDateTimeChanged(date) {
        if (!areDateEquals(this.date || "", date)) {
            if (date.locale === "th-TH") {
                this.props.update(date.minus({years: 543}));
            } else {
                this.props.update(date);
            }
        }
    },
});
