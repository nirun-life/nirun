/** @odoo-module **/

import {KanbanRecord} from "@web/views/kanban/kanban_record";
import {patch} from "web.utils";
import {registry} from "@web/core/registry";

const formatters = registry.category("formatters");

/**
 * Returns a "raw" version of the field value on a given record.
 *
 * @param {Record} record
 * @param {String} fieldName
 * @returns {any}
 */
function getRawValue(record, fieldName) {
    const field = record.fields[fieldName];
    const value = record.data[fieldName];
    switch (field.type) {
        case "one2many":
        case "many2many": {
            return value.count ? value.currentIds : [];
        }
        case "many2one": {
            return (value && value[0]) || false;
        }
        case "date":
        case "datetime": {
            return value && value.toISO();
        }
        default: {
            return value;
        }
    }
}

/**
 * Returns a formatted version of the field value on a given record.
 *
 * @param {Record} record
 * @param {String} fieldName
 * @returns {String}
 */
function getFormattedValue(record, fieldName) {
    const field = record.fields[fieldName];
    let value = record.data[fieldName];
    const formatter = formatters.get(field.type, String);
    if (field.type === "date" || field.type === "datetime") {
        if (value.locale === "th-TH") {
            value = value.plus({years: 543});
        }
    }
    return formatter(value, {field, data: record.data});
}

/**
 * Checks if a html content is empty. If there are only formatting tags
 * with style attributes or a void content. Famous use case is
 * '<p style="..." class=".."><br></p>' added by some web editor(s).
 * Note that because the use of this method is limited, we ignore the cases
 * like there's one <img> tag in the content. In such case, even if it's the
 * actual content, we consider it empty.
 *
 * @param {String} innerHTML
 * @returns {Boolean} true if no content found or if containing only formatting tags
 */
function isHtmlEmpty(innerHTML = "") {
    const div = Object.assign(document.createElement("div"), {innerHTML});
    return div.innerText.trim() === "";
}

patch(KanbanRecord.prototype, "l10n_th_web_buddhist_calendar.kanban_record", {
    createRecordAndWidget(props) {
        const {archInfo, list, record} = props;
        const {activeActions} = archInfo;

        this.record = Object.create(null);
        for (const fieldName in record.data) {
            this.record[fieldName] = {
                get value() {
                    // ------Override start
                    return getFormattedValue(record, fieldName);
                    // ------Override end
                },
                get raw_value() {
                    return getRawValue(record, fieldName);
                },
            };
        }

        // Widget
        const deletable = activeActions.delete && (!list.groupedBy || !list.groupedBy("m2m"));
        const editable = activeActions.edit;
        this.widget = {
            deletable,
            editable,
            isHtmlEmpty,
        };
    },
});
