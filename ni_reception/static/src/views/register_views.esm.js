/** @odoo-module **/
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

import {KanbanController} from "@web/views/kanban/kanban_controller";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {ListController} from "@web/views/list/list_controller";
import {listView} from "@web/views/list/list_view";

const {onWillStart, useComponent} = owl;

export function useRegisterButton() {
    const component = useComponent();
    const user = useService("user");
    const action = useService("action");

    onWillStart(async () => {
        component.isManager = await user.hasGroup("ni_patient.group_manager");
    });

    component.onClickRegister = () => {
        action.doAction({
            name: "Patient Register",
            type: "ir.actions.act_window",
            res_model: "ni.patient",
            target: "new",
            views: [[false, "form"]],
            context: {is_modal: true},
        });
    };
}

export class ReceptionListController extends ListController {
    setup() {
        super.setup();
        useRegisterButton();
    }
}

registry.category("views").add("ni_reception_register_tree", {
    ...listView,
    Controller: ReceptionListController,
    buttonTemplate: "ni_reception.ListView.buttons",
});

export class ReceptionKanbanController extends KanbanController {
    setup() {
        super.setup();
        useRegisterButton();
    }
}
registry.category("views").add("ni_reception_register_kanban", {
    ...kanbanView,
    Controller: ReceptionKanbanController,
    buttonTemplate: "ni_reception.KanbanView.buttons",
});
