/** @odoo-module **/
import {CalendarDatePicker} from "@web/views/calendar/date_picker/calendar_date_picker";
import {patch} from "web.utils";
import {session} from "@web/session";

/* eslint-disable */
const {Info} = luxon;
/* eslint-enable */

patch(CalendarDatePicker.prototype, "l10n_th_web_buddhist_calendar.calendar_date_picker", {
    get options() {
        // This is needed because luxon gives the week in ISO format : Monday is the first day of the week.
        // (M T W T F S S) but the jsquery datepicker wants as day name option in US format (S M T W T F S)
        const weekdays = Array.from(Info.weekdays("narrow"));
        const last = weekdays.pop();
        return {
            dayNamesMin: [last, ...weekdays],
            firstDay: (this.props.model.firstDayOfWeek || 0) % 7,
            monthNames: Info.months("short"),
            onSelect: this.onDateSelected.bind(this),
            showOtherMonths: true,
            dateFormat: "yy-mm-dd",
            locale: session.user_context.lang.replace("_", "-"),
            // Send user locale to jquery ui datepicker
        };
    },
});
