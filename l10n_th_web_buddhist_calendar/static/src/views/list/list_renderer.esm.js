/** @odoo-module **/

import {ListRenderer} from "@web/views/list/list_renderer";
import {patch} from "web.utils";
import {registry} from "@web/core/registry";

const formatters = registry.category("formatters");

patch(ListRenderer.prototype, "l10n_th_web_buddhist_calendar.list_renderer", {
    getFormattedValue(column, record) {
        const fieldName = column.name;
        const field = this.fields[fieldName];
        const formatter = formatters.get(field.type, (val) => val);
        const formatOptions = {
            escape: false,
            data: record.data,
            isPassword: "password" in column.rawAttrs,
            digits: column.rawAttrs.digits ? JSON.parse(column.rawAttrs.digits) : field.digits,
            field: record.fields[fieldName],
        };
        let data = record.data[fieldName];
        if (field.type === "date" || field.type === "datetime") {
            if (data.locale === "th-TH") {
                data = data.plus({years: 543});
            }
        }
        return formatter(data, formatOptions);
    },
});
