/** @odoo-module **/

import {luxonToMoment, luxonToMomentFormat} from "@web/core/l10n/dates";
import {DatePicker} from "@web/core/datepicker/datepicker";
import {patch} from "web.utils";
import {session} from "@web/session";

/* eslint-disable */
const {DateTime} = luxon;
/* eslint-enable */

/**
 * @param {unknown} value1
 * @param {unknown} value2
 */
function areEqual(value1, value2) {
    if (value1 && value2) {
        // Only compare date values
        return Number(value1) === Number(value2);
    }
    return value1 === value2;
}

patch(DatePicker.prototype, "l10n_th_web_buddhist_calendar.datepicker", {
    updateInput({useStatic} = {}) {
        /*
        Will be called when field is not on Read-Only state
        'this.date' was updated by this.props.update() at Date{Time}Field.onDateTimeChanged(date)
        */
        let date = this.date;
        if (date.locale === "th-TH") {
            // FormattedDate will be different from commonDate when it is Thai Locale
            date = date.plus({year: 543});
        }
        const [commonDate] = this.formatValue(this.date, this.getOptions(useStatic));
        const [formattedDate] = this.formatValue(date, this.getOptions(useStatic));

        if (formattedDate !== null) {
            // Update display format of DatePicker's input (Not on calendar picker)
            this.inputRef.el.value = formattedDate;
            // Update at Widget level with CE date
            this.props.onUpdateInput(commonDate);
        }
    },
    onDateChange() {
        const [value, error] = this.isPickerChanged
            ? [this.pickerDate, null]
            : this.parseValue(this.inputRef.el.value, this.getOptions());
        // L10n_th_web_buddhist_calendar FIX START !!
        // we minus value on input field user's lang is thai
        let _value = value;
        if (value && !this.isPickerChanged && session.user_context.lang === "th_TH") {
            _value = value.minus({year: 543});
        }
        this.state.warning = _value && _value > DateTime.local();

        if (error || areEqual(this.date, _value)) {
            // Force current value
            this.updateInput(this.date);
        } else {
            this.props.onDateTimeChanged(_value);
        }
        // L10n_th_web_buddhist_calendar FIX END !!

        if (this.pickerDate) {
            this.inputRef.el.select();
        }
    },
    bootstrapDateTimePicker(commandOrParams, ...commandArgs) {
        if (typeof commandOrParams === "object") {
            const params = {
                ...commandOrParams,
                date: this.date || null,
                format: luxonToMomentFormat(this.staticFormat),
                // L10n_th_web_buddhist_calendar FIX START !!
                // set user's lang as default locale for DateTimePicker
                locale: commandOrParams.locale || session.user_context.lang.replace("_", "-"),
                // L10n_th_web_buddhist_calendar FIX END !!
            };
            for (const prop in params) {
                if (params[prop] instanceof DateTime) {
                    params[prop] = luxonToMoment(params[prop]);
                }
            }
            commandOrParams = params;
            console.log(commandOrParams);
        }
        window.$(this.rootRef.el).datetimepicker(commandOrParams, ...commandArgs);
    },
});
