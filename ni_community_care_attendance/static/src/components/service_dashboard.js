/** @odoo-module */

import {useService} from "@web/core/utils/hooks";
import {formatMonetary} from "@web/views/fields/formatters";

const {Component, onWillStart, useState} = owl;

export class ServiceEventDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({types: {}});

        onWillStart(async () => {
            const employee_dashboard = await this.orm.call("ni.employee.report", "get_employee_dashboard", []);
            this.state.types = employee_dashboard;
        });
    }

    renderMonetaryField(value, currency_id) {
        return formatMonetary(value, {currencyId: currency_id});
    }
}

ServiceEventDashboard.template = "ni_community_care_attendance.ServiceEventDashboard";
