/*
 * Observation lines with sections and notes. Re-ported from core
 * account/static/src/components/section_and_note_fields_backend (18.0), plus:
 * - the title field is "title";
 * - only the value column matching the line's value_type is shown, spanning the
 *   hidden ones.
 */
import {Component, useEffect} from "@odoo/owl";
import {ListTextField, TextField} from "@web/views/fields/text/text_field";
import {X2ManyField, x2ManyField} from "@web/views/fields/x2many/x2many_field";
import {CharField} from "@web/views/fields/char/char_field";
import {ListRenderer} from "@web/views/list/list_renderer";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

const VALUE_COLUMNS = [
    "value_char",
    "value_int",
    "value_float",
    "value_code_id",
    "value_code_ids",
];

export class SectionAndNoteListRenderer extends ListRenderer {
    static template = "ni_observation.sectionAndNoteListRenderer";

    setup() {
        super.setup();
        this.titleField = "title";
        useEffect(
            (editedRecord) => this.focusToName(editedRecord),
            () => [this.editedRecord]
        );
    }

    focusToName(editRec) {
        if (editRec && editRec.isNew && this.isSectionOrNote(editRec)) {
            const col = this.columns.find((c) => c.name === this.titleField);
            this.focusCell(col, null);
        }
    }

    isValueColumn(column) {
        return VALUE_COLUMNS.includes(column.name);
    }

    isSectionOrNote(record = null) {
        record = record || this.record;
        return ["line_section", "line_note"].includes(record.data.display_type);
    }

    getRowClass(record) {
        const existingClasses = super.getRowClass(record);
        return `${existingClasses} o_is_${record.data.display_type}`;
    }

    getCellClass(column, record) {
        const classNames = super.getCellClass(column, record);
        const isValueColumnMismatch =
            this.isValueColumn(column) &&
            column.name !== `value_${record.data.value_type}`;
        const isHiddenSectionOrNote =
            this.isSectionOrNote(record) &&
            column.widget !== "handle" &&
            column.name !== this.titleField;
        const isHiddenTitleField =
            !this.isSectionOrNote(record) && column.name === this.titleField;
        if (isValueColumnMismatch || isHiddenSectionOrNote || isHiddenTitleField) {
            return `${classNames} o_hidden`;
        }
        return classNames;
    }

    getColumns(record) {
        const columns = super.getColumns(record);
        if (this.isSectionOrNote(record)) {
            return this.getSectionColumns(columns);
        }
        const hideCols = columns.filter(
            (col) =>
                col.name === this.titleField ||
                (this.isValueColumn(col) &&
                    col.name !== `value_${record.data.value_type}`)
        );
        const showCols = columns.filter((col) => !hideCols.includes(col));
        return showCols.map((col) => {
            if (this.isValueColumn(col)) {
                return {...col, colspan: hideCols.length + 1};
            }
            return {...col};
        });
    }

    getSectionColumns(columns) {
        const sectionCols = columns.filter(
            (col) =>
                col.widget === "handle" ||
                (col.type === "field" && col.name === this.titleField)
        );
        return sectionCols.map((col) => {
            if (col.name === this.titleField) {
                return {...col, colspan: columns.length - sectionCols.length + 1};
            }
            return {...col};
        });
    }
}
export class SectionAndNoteFieldOne2Many extends X2ManyField {
    static components = {
        ...X2ManyField.components,
        ListRenderer: SectionAndNoteListRenderer,
    };
}

export class SectionAndNoteText extends Component {
    static template = "ni_observation.SectionAndNoteText";
    static props = {...standardFieldProps};

    get componentToUse() {
        return this.props.record.data.display_type === "line_section"
            ? CharField
            : TextField;
    }
}

export class ListSectionAndNoteText extends SectionAndNoteText {
    get componentToUse() {
        return this.props.record.data.display_type !== "line_section"
            ? ListTextField
            : super.componentToUse;
    }
}

export const sectionAndNoteFieldOne2Many = {
    ...x2ManyField,
    component: SectionAndNoteFieldOne2Many,
    additionalClasses: [...(x2ManyField.additionalClasses || []), "o_field_one2many"],
};

export const sectionAndNoteText = {
    component: SectionAndNoteText,
    additionalClasses: ["o_field_text"],
};

export const listSectionAndNoteText = {
    ...sectionAndNoteText,
    component: ListSectionAndNoteText,
};

registry
    .category("fields")
    .add("ob_section_and_note_one2many", sectionAndNoteFieldOne2Many);
registry.category("fields").add("ob_section_and_note_text", sectionAndNoteText);
registry
    .category("fields")
    .add("list.ob_section_and_note_text", listSectionAndNoteText);
