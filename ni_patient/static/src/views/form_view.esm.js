import {FormController} from "@web/views/form/form_controller";
import {formView} from "@web/views/form/form_view";
import {registry} from "@web/core/registry";
import {useArchivePatient} from "@ni_patient/views/archive_patient_hook.esm";

export class PatientFormController extends FormController {
    setup() {
        super.setup();
        this.archivePatient = useArchivePatient();
    }

    getStaticActionMenuItems() {
        const menuItems = super.getStaticActionMenuItems();
        if (menuItems.archive) {
            menuItems.archive.callback = () =>
                this.archivePatient([this.model.root.resId]);
        }
        return menuItems;
    }
}

registry.category("views").add("ni_patient_form", {
    ...formView,
    Controller: PatientFormController,
});
