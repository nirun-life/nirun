/** @odoo-module */

import {PatientDashboard} from "../components/patient_dashboard";
import {ServiceEventApprovalDashboard, ServiceEventDashboard} from "../components/service_dashboard";

import {registry} from "@web/core/registry";
import {listView} from "@web/views/list/list_view";
import {ListRenderer} from "@web/views/list/list_renderer";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {KanbanRenderer} from "@web/views/kanban/kanban_renderer";
import {Component} from "@odoo/owl";

export class ServiceEventDashboardField extends Component {}
ServiceEventDashboardField.components = {ServiceEventApprovalDashboard};
ServiceEventDashboardField.template = "ni_community_care.ServiceEventApprovalDashboardField";

registry.category("fields").add("service_event_approval_dashboard", ServiceEventDashboardField);

export class PatientListRenderer extends ListRenderer {}
PatientListRenderer.components = {...PatientListRenderer.components, PatientDashboard, ServiceEventDashboard};
PatientListRenderer.template = "ni_community_care.DashboardListRenderer";
registry.category("views").add("patient_dashboard_tree", {
    ...listView,
    Renderer: PatientListRenderer,
});

export class PatientKanbanRenderer extends KanbanRenderer {}
PatientKanbanRenderer.components = {...PatientKanbanRenderer.components, PatientDashboard, ServiceEventDashboard};
PatientKanbanRenderer.template = "ni_community_care.DashboardKanbanRenderer";
registry.category("views").add("patient_dashboard_kanban", {
    ...kanbanView,
    Renderer: PatientKanbanRenderer,
});
