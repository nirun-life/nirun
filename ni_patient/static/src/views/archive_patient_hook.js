/** @odoo-module **/

import {useService} from "@web/core/utils/hooks";
const {useComponent, useEnv} = owl;

export function useArchivePatient() {
    const component = useComponent();
    const env = useEnv();
    const action = useService("action");

    return (id) => {
        action.doAction(
            {
                type: "ir.actions.act_window",
                name: env._t("Patient Archive"),
                res_model: "ni.patient.archive.wizard",
                view_mode: "form",
                views: [[false, "form"]],
                target: "new",
                context: {
                    default_patient_id: id,
                    toggle_active: true,
                },
            },
            {
                onClose: async () => {
                    await component.model.load();
                    component.model.notify();
                },
            }
        );
    };
}
