from odoo import models


class PatientStateReason(models.Model):
    _name = "ni.patient.state.reason"
    _description = "Patient State Reason"
    _inherit = ["ni.coding"]
    #
    # name = fields.Char(string="Reason", required=True)
    # code = fields.Selection(
    #     [
    #         ("deceased", "เสียชีวิต"),
    #         ("moved_away", "ออกจากพื้นที่"),
    #         ("other", "อื่นๆ"),
    #     ],
    #     string="Reason Code",
    #     required=True,
    # )
    # active = fields.Boolean(default=True)
