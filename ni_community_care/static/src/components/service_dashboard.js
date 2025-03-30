/** @odoo-module */

import {useService} from "@web/core/utils/hooks";
import {formatMonetary} from "@web/views/fields/formatters";

const {Component, onWillStart, useState} = owl;

export class ServiceEventDashboard extends Component {
    setup() {
        super.setup();
        this.orm = useService("orm");

        this.state = useState({
            types: {},
        });

        onWillStart(async () => {
            const patient_types = await this.orm.call("ni.service.event.report", "get_patient_type_dashboard", []);
            this.state.types = patient_types;
        });
    }

    renderMonetaryField(value, currency_id) {
        return formatMonetary(value, {currencyId: currency_id});
    }
}
ServiceEventDashboard.template = "ni_community_care.ServiceEventDashboard";
