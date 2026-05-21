/** @odoo-module **/

import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {ListController} from "@web/views/list/list_controller";
import {listView} from "@web/views/list/list_view";

const WIZARD_ACTION = {
    name: "New Care Plan",
    type: "ir.actions.act_window",
    res_model: "ni.careplan.wizard",
    target: "new",
    views: [[false, "form"]],
};

export class CareplanListController extends ListController {
    setup() {
        super.setup();
        this.actionService = useService("action");
    }

    onClickNewCareplan() {
        this.actionService.doAction(WIZARD_ACTION);
    }
}

registry.category("views").add("ni_careplan_tree", {
    ...listView,
    Controller: CareplanListController,
    buttonTemplate: "ni_careplan.ListView.buttons",
});

export class CareplanKanbanController extends KanbanController {
    setup() {
        super.setup();
        this.actionService = useService("action");
    }

    onClickNewCareplan() {
        this.actionService.doAction(WIZARD_ACTION);
    }
}

registry.category("views").add("ni_careplan_kanban", {
    ...kanbanView,
    Controller: CareplanKanbanController,
    buttonTemplate: "ni_careplan.KanbanView.buttons",
});
