/** @odoo-module **/

import {areDateEquals, formatDate, formatDateTime} from "@web/core/l10n/dates";
import {DateField} from "@web/views/fields/date/date_field";
import {localization} from "@web/core/l10n/localization";
import {patch} from "web.utils";

patch(DateField.prototype, "l10n_th_web_buddhist_calendar.date_field", {
    get formattedValue() {
        let date = this.props.value;
        if (date.locale === "th-TH") {
            date = date.plus({year: 543});
        }
        return this.isDateTime ? formatDateTime(date, {format: localization.dateFormat}) : formatDate(date);
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
