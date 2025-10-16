import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ReportServiceEventApproval(models.AbstractModel):
    _name = "report.ni_community_care.approval_category_report_template"
    _description = "Report: Service Event Approval Category"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["ni.service.event.approval"].browse(docids)

        data = data or {}
        ctx_data = self.env.context.get("custom_patient_data")
        if ctx_data:
            data["custom_patient_data"] = ctx_data

        _logger.info(
            "[REPORT] _get_report_values called | docids=%s | data_keys=%s",
            docids,
            list(data.keys()) if data else "None",
        )

        return {
            "doc_ids": docids,
            "doc_model": "ni.service.event.approval",
            "docs": docs,
            "data": data,
        }
