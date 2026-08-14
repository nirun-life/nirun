/** @odoo-module **/

import {registry} from "@web/core/registry";
import {formView} from "@web/views/form/form_view";
import {FormController} from "@web/views/form/form_controller";

import {useArchivePatient} from "@ni_patient/views/archive_patient_hook";

export class PatientFormController extends FormController {
    setup() {
        super.setup();
        this.archivePatient = useArchivePatient();
    }

    getActionMenuItems() {
        const menuItems = super.getActionMenuItems();
        if (!this.archiveEnabled || !this.model.root.isActive) {
            return menuItems;
        }
        const archiveAction = menuItems.other.find((item) => item.key === "archive");
        if (archiveAction) {
            archiveAction.callback = () => this.archivePatient([this.model.root.resId]);
        }
        return menuItems;
    }
}

registry.category("views").add("ni_patient_form", {
    ...formView,
    Controller: PatientFormController,
});
