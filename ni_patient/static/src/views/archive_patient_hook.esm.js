import {_t} from "@web/core/l10n/translation";
import {useComponent} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";

export function useArchivePatient() {
    const component = useComponent();
    const action = useService("action");

    return (resIds) => {
        action.doAction(
            {
                type: "ir.actions.act_window",
                name: _t("Patient Archive"),
                res_model: "ni.patient.archive.wizard",
                view_mode: "form",
                views: [[false, "form"]],
                target: "new",
                context: {
                    default_patient_ids: resIds,
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
