/** @odoo-module */

import {ServiceEventDashboard} from "../components/service_dashboard";

import {registry} from "@web/core/registry";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {KanbanRenderer} from "@web/views/kanban/kanban_renderer";

// Custom Kanban Renderer → renamed to EmployeeKanbanRenderer
export class EmployeeKanbanRenderer extends KanbanRenderer {}
EmployeeKanbanRenderer.components = {
    ...EmployeeKanbanRenderer.components,
    ServiceEventDashboard,
};
EmployeeKanbanRenderer.template = "ni_community_care_attendance.DashboardKanbanRenderer";

registry.category("views").add("employee_dashboard_kanban", {
    ...kanbanView,
    Renderer: EmployeeKanbanRenderer,
});
