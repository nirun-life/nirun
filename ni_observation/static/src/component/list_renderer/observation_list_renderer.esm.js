/** @odoo-module **/

import {registry} from "@web/core/registry";
import {ListRenderer} from "@web/views/list/list_renderer";
import {X2ManyField} from "@web/views/fields/x2many/x2many_field";
import {ListTextField, TextField} from "@web/views/fields/text/text_field";
import {CharField} from "@web/views/fields/char/char_field";

const {Component, useEffect} = owl;

export class SectionAndNoteListRenderer extends ListRenderer {
    /**
     * The purpose of this extension is to allow sections and notes in the one2many list
     * primarily used on Sales Orders and Invoices
     *
     * @override
     */
    setup() {
        super.setup();
        this.titleField = "name";
        useEffect(
            () => this.focusToName(this.props.list.editedRecord),
            () => [this.props.list.editedRecord]
        );
    }

    focusToName(editRec) {
        if (editRec && editRec.isVirtual && this.isSectionOrNote(editRec)) {
            const col = this.state.columns.find((c) => c.name === this.titleField);
            this.focusCell(col, null);
        }
    }

    isValueColumn(column) {
        return ["value_char", "value_int", "value_float", "value_code_id", "value_code_ids"].includes(column.name);
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
        const isValueColumnMismatch = this.isValueColumn(column, record) && column.name !== `value_${record.data.value_type}`;
        const isHiddenSectionOrNote =
            this.isSectionOrNote(record) && column.widget !== "handle" && column.name !== this.titleField;
        const isHiddenTitleField = !this.isSectionOrNote(record) && column.name === this.titleField;
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
            (col) => col.name === this.titleField || (this.isValueColumn(col) && col.name !== `value_${record.data.value_type}`)
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
            (col) => col.widget === "handle" || (col.type === "field" && col.name === this.titleField)
        );
        return sectionCols.map((col) => {
            if (col.name === this.titleField) {
                return {...col, colspan: columns.length - sectionCols.length + 1};
            }
            return {...col};
        });
    }
}
SectionAndNoteListRenderer.template = "ni_observation.sectionAndNoteListRenderer";

export class SectionAndNoteFieldOne2Many extends X2ManyField {}
SectionAndNoteFieldOne2Many.additionalClasses = ["o_field_one2many"];
SectionAndNoteFieldOne2Many.components = {
    ...X2ManyField.components,
    ListRenderer: SectionAndNoteListRenderer,
};

export class SectionAndNoteText extends Component {
    get componentToUse() {
        return this.props.record.data.display_type === "line_section" ? CharField : TextField;
    }
}
SectionAndNoteText.template = "ni_observation.SectionAndNoteText";
SectionAndNoteText.additionalClasses = ["o_field_text"];

export class ListSectionAndNoteText extends SectionAndNoteText {
    get componentToUse() {
        return this.props.record.data.display_type !== "line_section" ? ListTextField : super.componentToUse;
    }
}

registry.category("fields").add("ob_section_and_note_one2many", SectionAndNoteFieldOne2Many);
registry.category("fields").add("ob_section_and_note_text", SectionAndNoteText);
registry.category("fields").add("list.ob_section_and_note_text", ListSectionAndNoteText);
