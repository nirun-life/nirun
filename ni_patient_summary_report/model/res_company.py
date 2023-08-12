#  Copyright (c) 2023 NSTDA

from odoo import _, fields, models

APPEND = _(
    """
<h5>Recommendation</h5>
<ul class="o_checklist">
    <li id="checkId-1">Patient need rest for ........................ day</li>
    <li id="checkId-2">Patient has received treatment in the hospital</li>
</ul>
"""
)


class Company(models.Model):
    _inherit = "res.company"

    med_cert_diagnosis = fields.Selection(
        [("none", "No Show"), ("first", "Show First"), ("all", "Show All")],
        "Diagnosis",
        default="none",
        required=True,
    )
    med_cert_append = fields.Html("Append", default=APPEND, translate=True)
