/** @odoo-module **/

import {DatePicker} from "@web/core/datepicker/datepicker";
import {patch} from "web.utils";

patch(DatePicker.prototype, "l10n_th_web_buddhist_calendar.datepicker", {
    updateInput({useStatic} = {}) {
        let date = this.date;
        if (date.locale === "th-TH") {
            date = date.plus({year: 543});
        }
        const [formattedDate] = this.formatValue(date, this.getOptions(useStatic));
        if (formattedDate !== null) {
            this.inputRef.el.value = formattedDate;
            this.props.onUpdateInput(formattedDate);
        }
    },
});
