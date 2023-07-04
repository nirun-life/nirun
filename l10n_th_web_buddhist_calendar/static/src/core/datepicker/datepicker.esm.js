/** @odoo-module **/

import {luxonToMoment, luxonToMomentFormat} from "@web/core/l10n/dates";
import {DatePicker} from "@web/core/datepicker/datepicker";
import {patch} from "web.utils";
import {session} from "@web/session";

/* eslint-disable */
const {DateTime} = luxon;
/* eslint-enable */

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
    // Call getDefaultDate() when field have no value to get BE as default
    bootstrapDateTimePicker(commandOrParams) {
        if (typeof commandOrParams === "object") {
            const format = this.isValidStaticFormat(this.format) ? this.format : this.staticFormat;
            const params = {
                ...commandOrParams,
                date: this.date || this.getDefaultDate(commandOrParams),
                format: luxonToMomentFormat(format),
                locale: commandOrParams.locale || (this.date && this.date.locale),
            };
            for (const prop in params) {
                if (params[prop] instanceof DateTime) {
                    params[prop] = luxonToMoment(params[prop]);
                }
            }
            commandOrParams = params;
        }
        return window.$(this.rootRef.el).datetimepicker(commandOrParams);
    },
    getDefaultDate(commandOrParams) {
        var locale = commandOrParams.locale || session.user_context.lang.replace("_", "-");
        if (this.date === false && locale === "th-TH") {
            return DateTime.now().plus({year: 543});
        }
        return null;
    },
});
