#  Copyright (c) 2026 NSTDA
from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ObservationWizard(models.TransientModel):
    _name = "ni.observation.wizard"
    _description = "Observation Wizard"

    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    patient_id = fields.Many2one(
        "ni.patient", required=True, domain=[("company_id", "=", company_id)]
    )
    encounter_id = fields.Many2one(
        "ni.encounter", domain=[("parent_id", "=", patient_id)]
    )
    type = fields.Selection(
        [
            ("new", "New"),
            ("edit", "Edit"),
        ],
        default="new",
        required=True,
    )
    category_ids = fields.Many2many(
        "ni.observation.category", domain="[('type_count', '>', 0)]"
    )
    state = fields.Selection(
        [("1", "1. Category"), ("2", "2. Observation")], default="1", required=True
    )
    sheet_id = fields.Many2one(
        "ni.observation.sheet",
        domain="[('patient_id', '=?', patient_id), ('encounter_id', '=?', encounter_id)]",
    )
    init_occurrence = fields.Datetime(default=fields.Datetime.now)
    occurrence = fields.Datetime(related="sheet_id.occurrence")
    sheet_create_uid = fields.Many2one(related="sheet_id.create_uid")
    sheet_create_date = fields.Datetime(related="sheet_id.create_date")
    observation_ids = fields.One2many(
        related="sheet_id.observation_ids", readonly=False
    )
    note = fields.Text(related="sheet_id.note", readonly=False)

    def prepare_sheet(self):
        if not len(self.category_ids):
            raise ValidationError(_("Please specify at least one category"))

        sheet = self.env["ni.observation.sheet"].create(
            {"occurrence": self.init_occurrence, "category_ids": self.category_ids.ids}
        )
        sheet.action_line_by_category_ids()
        self.write(
            {
                "patient_id": self.patient_id.id,
                "encounter_id": self.encounter_id.id,
                "sheet_id": sheet.id,
                "state": "2",
            }
        )
        return {
            "name": f"{self._description} - {sheet.identifier}",
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
        }

    def next_state(self):
        self.state = "2"
        return {
            "name": f"{self._description} - {self.sheet_id.identifier}",
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
        }

    def submit_sheet(self):
        self.sheet_id.observation_ids.garbage_collect()

    def discard_sheet(self):
        self.sheet_id.unlink()
