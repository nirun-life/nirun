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

export class ServiceEventApprovalDashboard extends Component {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.state = useState({
            types: {},
        });

        // ระบุให้ไม่แสดงหัวข้อ
        this.hideTitle = true;

        const recordId = this.env.model.root.resId;
        if (recordId) {
            onWillStart(async () => {
                const patient_types = await this.orm.call("ni.service.event.approval", "get_patient_type_dashboard", [
                    recordId,
                ]);
                this.state.types = patient_types;
            });
        }
    }

    renderMonetaryField(value, currency_id) {
        return formatMonetary(value, {currencyId: currency_id});
    }
}
ServiceEventApprovalDashboard.template = "ni_community_care.ServiceEventDashboard";
