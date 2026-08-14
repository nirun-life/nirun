/** @odoo-module **/

import {registry} from "@web/core/registry";
import {listView} from "@web/views/list/list_view";
import {ListController} from "@web/views/list/list_controller";

import {useArchivePatient} from "@ni_patient/views/archive_patient_hook";

export class PatientListController extends ListController {
    setup() {
        super.setup();
        this.archivePatient = useArchivePatient();
    }

    getActionMenuItems() {
        const menuItems = super.getActionMenuItems();
        if (!this.archiveEnabled) {
            return menuItems;
        }
        const archiveAction = menuItems.other.find((item) => item.key === "archive");
        if (archiveAction) {
            // ข้าม ConfirmationDialog ของ Odoo ไปใช้ wizard แทน
            // ponytail: "เลือกทั้งหมด" ส่ง id ได้ถึง active_ids_limit (20000)
            // ระดับนั้น dialog ค้าง (m2m write + name_get + DOM tag อย่างละ 20k)
            // ถ้าเจอจริง: ใส่ limit หรือเลิกโชว์ tag ใช้ patient_count เป็นข้อความแทน
            archiveAction.callback = async () => this.archivePatient(await this.getSelectedResIds());
        }
        return menuItems;
    }
}

registry.category("views").add("ni_patient_list", {
    ...listView,
    Controller: PatientListController,
});
