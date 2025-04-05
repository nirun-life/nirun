/** @odoo-module **/

import {formatDate, formatDateTime} from "@web/core/l10n/dates";
import {DateField} from "@web/views/fields/date/date_field";
import {localization} from "@web/core/l10n/localization";
import {patch} from "web.utils";

patch(DateField.prototype, "l10n_th_web_buddhist_calendar.date_field", {
    get formattedValue() {
        /** This method will only be called when field state is Read-Only . otherwise this have no affect **/
        let date = this.props.value;
        if (date.locale === "th-TH") {
            date = date.plus({year: 543});
        }
        return this.isDateTime ? formatDateTime(date, {format: localization.dateFormat}) : formatDate(date);
    },
});
