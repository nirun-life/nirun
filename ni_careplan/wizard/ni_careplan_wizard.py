#  Copyright (c) 2025 NSTDA

from odoo import api, fields, models
from odoo.tools.date_utils import relativedelta


class CareplanWizardObsLine(models.TransientModel):
    _name = "ni.careplan.wizard.obs.line"
    _description = "Careplan Wizard Observation Line"

    wizard_id = fields.Many2one("ni.careplan.wizard", required=True, ondelete="cascade")
    patient_id = fields.Many2one(related="wizard_id.patient_id")
    observation_type_id = fields.Many2one(
        "ni.observation.type", required=True, string="Observation Type"
    )
    observation_id = fields.Many2one(
        "ni.observation",
        string="Observation",
        domain="[('patient_id', '=', patient_id), ('type_id', '=', observation_type_id)]",
    )
    occurrence = fields.Datetime(
        related="observation_id.occurrence", readonly=True, string="Date"
    )
    selected = fields.Boolean(default=False)

    @api.onchange("observation_type_id")
    def _onchange_observation_type_id(self):
        for rec in self:
            if not rec.observation_type_id or not rec.wizard_id.patient_id:
                rec.observation_id = False
                continue
            latest = self.env["ni.observation"].search(
                [
                    ("patient_id", "=", rec.wizard_id.patient_id.id),
                    ("type_id", "=", rec.observation_type_id.id),
                ],
                order="occurrence desc",
                limit=1,
            )
            rec.observation_id = latest or False
            rec.selected = bool(latest)


class CareplanWizardGoalLine(models.TransientModel):
    _name = "ni.careplan.wizard.goal.line"
    _description = "Careplan Wizard Goal Line"

    wizard_id = fields.Many2one("ni.careplan.wizard", required=True, ondelete="cascade")
    goal_code_id = fields.Many2one("ni.goal.code")
    name = fields.Char("Goal Name")
    observation_type_id = fields.Many2one("ni.observation.type", string="Measure")
    target_min = fields.Float("Min", default=0.0)
    target_max = fields.Float("Max", default=100.0)
    selected = fields.Boolean(default=True)

    @api.onchange("goal_code_id")
    def _onchange_goal_code_id(self):
        for rec in self:
            if not rec.goal_code_id:
                continue
            g = rec.goal_code_id
            rec.name = g.name
            rec.observation_type_id = g.observation_type_id
            if g.observation_type_id:
                if g.target_type == "fix":
                    rec.target_min = g.target_fix_min
                    rec.target_max = g.target_fix_max


class CareplanWizardServiceLine(models.TransientModel):
    _name = "ni.careplan.wizard.service.line"
    _description = "Careplan Wizard Service Line"

    wizard_id = fields.Many2one("ni.careplan.wizard", required=True, ondelete="cascade")
    template_service_id = fields.Many2one("ni.careplan.template.service.request")
    name = fields.Char("Service Name")
    category_id = fields.Many2one("ni.service.category")
    service_ids = fields.Many2many(
        "ni.service",
        "ni_careplan_wizard_service_line_service_rel",
        "line_id",
        "service_id",
    )
    timing_tmpl_id = fields.Many2one("ni.timing.template")
    selected = fields.Boolean(default=True)

    @api.onchange("service_ids")
    def _onchange_service_ids(self):
        for rec in self:
            if rec.service_ids and not rec.name:
                name = ", ".join(rec.service_ids.mapped("name"))
                rec.name = name[:128] if len(name) > 128 else name


class CareplanWizardMedicationLine(models.TransientModel):
    _name = "ni.careplan.wizard.medication.line"
    _description = "Careplan Wizard Medication Line"

    wizard_id = fields.Many2one("ni.careplan.wizard", required=True, ondelete="cascade")
    template_medication_id = fields.Many2one(
        "ni.careplan.template.medication.request", readonly=True
    )
    medication_id = fields.Many2one("ni.medication", required=True)
    quantity = fields.Float("Qty", default=1.0, required=True)
    note = fields.Char()
    selected = fields.Boolean(default=True)


class CareplanWizard(models.TransientModel):
    _name = "ni.careplan.wizard"
    _description = "Care Plan Wizard"

    state = fields.Selection(
        [
            ("1", "1. Diagnosis & Template"),
            ("2", "2. Observations"),
            ("3", "3. Goals"),
            ("4", "4. Interventions"),
            ("5", "5. Confirm"),
        ],
        default="1",
        required=True,
    )

    # Step 1
    patient_id = fields.Many2one(
        "ni.patient", required=True, domain="[('deceased', '=', False)]"
    )
    patient_age = fields.Integer(related="patient_id.age")
    patient_gender = fields.Selection(related="patient_id.gender")
    encounter_id = fields.Many2one(
        "ni.encounter",
        domain="[('patient_id', '=', patient_id)]",
    )
    condition_ids = fields.Many2many(
        "ni.condition",
        "ni_careplan_wizard_condition_rel",
        "wizard_id",
        "condition_id",
        domain="[('patient_id', '=', patient_id), ('clinical_state', '=', 'active')]",
        string="Diagnosis",
    )
    template_id = fields.Many2one(
        "ni.careplan.template",
        domain="[('category_id', '=?', category_id)]",
    )
    category_id = fields.Many2one("ni.careplan.category")

    # Step 2
    obs_line_ids = fields.One2many(
        "ni.careplan.wizard.obs.line", "wizard_id", string="Observations"
    )

    # Step 3
    goal_line_ids = fields.One2many(
        "ni.careplan.wizard.goal.line", "wizard_id", string="Goals"
    )

    # Step 4
    service_line_ids = fields.One2many(
        "ni.careplan.wizard.service.line", "wizard_id", string="Service Requests"
    )
    medication_line_ids = fields.One2many(
        "ni.careplan.wizard.medication.line", "wizard_id", string="Medications"
    )

    # Step 5
    period_start = fields.Datetime(string="Start", default=fields.Datetime.now)
    period_end = fields.Datetime(
        string="End",
        default=lambda self: fields.Datetime.now() + relativedelta(months=3),
    )
    save_as_draft = fields.Boolean(
        default=False,
        string="Save as Draft",
        help="Save the careplan in draft state instead of confirming immediately.",
    )

    @api.onchange("condition_ids")
    def _onchange_condition_ids(self):
        if not self.condition_ids:
            return
        condition_codes = self.condition_ids.mapped("code_id")
        if not condition_codes:
            return
        template = self.env["ni.careplan.template"].search(
            [("condition_code_ids", "parent_of", condition_codes.ids)],
            limit=1,
        )
        if template:
            self.template_id = template

    @api.onchange("template_id")
    def _onchange_template_id(self):
        if self.template_id and self.template_id.category_id:
            self.category_id = self.template_id.category_id

    def _reopen_wizard(self):
        context = dict(self.env.context)
        return {
            "name": self._description,
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "context": context,
            "target": "new",
        }

    def action_next_step1_to_2(self):
        self.ensure_one()
        self.obs_line_ids.unlink()
        type_ids = self.condition_ids.mapped("code_id.observation_code_ids")
        if self.template_id:
            type_ids |= self.template_id.observation_type_ids
        lines = []
        Observation = self.env["ni.observation"]
        for ob_type in type_ids:
            latest = Observation.search(
                [("patient_id", "=", self.patient_id.id), ("type_id", "=", ob_type.id)],
                order="occurrence desc",
                limit=1,
            )
            lines.append(
                {
                    "wizard_id": self.id,
                    "observation_type_id": ob_type.id,
                    "observation_id": latest.id if latest else False,
                    "selected": bool(latest),
                }
            )
        if lines:
            self.env["ni.careplan.wizard.obs.line"].create(lines)
        self.state = "2"
        return self._reopen_wizard()

    def action_next_step2_to_3(self):
        self.ensure_one()
        self.goal_line_ids.unlink()
        if self.template_id and self.template_id.goal_code_ids:
            condition_codes = self.condition_ids.mapped("code_id")
            relevant = self.template_id.goal_code_ids.filtered_domain(
                [
                    "|",
                    ("condition_code_ids", "=", False),
                    ("condition_code_ids", "child_of", condition_codes.ids),
                ]
            )
            lines = []
            for g in relevant:
                line_val = {
                    "wizard_id": self.id,
                    "goal_code_id": g.id,
                    "name": g.name,
                    "observation_type_id": g.observation_type_id.id or False,
                    "selected": True,
                }
                if g.observation_type_id:
                    if g.target_type == "fix":
                        line_val["target_min"] = g.target_fix_min
                        line_val["target_max"] = g.target_fix_max
                    elif g.target_type == "ratio":
                        obs_line = self.obs_line_ids.filtered(
                            lambda l, g=g: l.observation_type_id
                            == g.observation_type_id
                            and l.observation_id
                        )
                        if obs_line:
                            last_value = float(obs_line[0].observation_id.value or 0)
                            line_val["target_min"] = last_value * g.target_ratio_min
                            line_val["target_max"] = last_value * g.target_ratio_max
                lines.append(line_val)
            if lines:
                self.env["ni.careplan.wizard.goal.line"].create(lines)
        self.state = "3"
        return self._reopen_wizard()

    def action_next_step3_to_4(self):
        self.ensure_one()
        self.service_line_ids.unlink()
        self.medication_line_ids.unlink()
        if self.template_id:
            if self.template_id.service_request_ids:
                self.env["ni.careplan.wizard.service.line"].create(
                    [
                        {
                            "wizard_id": self.id,
                            "template_service_id": sr.id,
                            "name": sr.name,
                            "category_id": sr.category_id.id or False,
                            "service_ids": [fields.Command.set(sr.service_ids.ids)],
                            "timing_tmpl_id": sr.timing_tmpl_id.id or False,
                            "selected": True,
                        }
                        for sr in self.template_id.service_request_ids
                    ]
                )
            if self.template_id.medication_request_ids:
                self.env["ni.careplan.wizard.medication.line"].create(
                    [
                        {
                            "wizard_id": self.id,
                            "template_medication_id": med.id,
                            "medication_id": med.medication_id.id,
                            "quantity": med.quantity,
                            "note": med.note or False,
                            "selected": True,
                        }
                        for med in self.template_id.medication_request_ids
                    ]
                )
        self.state = "4"
        return self._reopen_wizard()

    def action_next_step4_to_5(self):
        self.ensure_one()
        self.state = "5"
        return self._reopen_wizard()

    def action_prev(self):
        self.ensure_one()
        state_map = {"2": "1", "3": "2", "4": "3", "5": "4"}
        self.state = state_map.get(self.state, "1")
        return self._reopen_wizard()

    def action_save_draft(self):
        return self.action_confirm(draft=True)

    def action_confirm(self, draft=False):
        self.ensure_one()
        careplan = self.env["ni.careplan"].create(
            {
                "patient_id": self.patient_id.id,
                "encounter_id": self.encounter_id.id or False,
                "category_id": self.category_id.id or False,
                "template_id": self.template_id.id or False,
                "condition_ids": [fields.Command.set(self.condition_ids.ids)],
                "period_start": self.period_start,
                "period_end": self.period_end,
                "intent": "plan",
            }
        )

        goal_vals = []
        for line in self.goal_line_ids.filtered("selected"):
            if line.goal_code_id:
                val = careplan._prepare_goal_value(
                    line.goal_code_id, self.condition_ids
                )
            else:
                val = {
                    "name": line.name or "/",
                    "patient_id": careplan.patient_id.id,
                    "encounter_id": careplan.encounter_id.id,
                    "careplan_id": careplan.id,
                    "state_id": self.env.ref("ni_goal.goal_state_active").id,
                    "condition_ids": [],
                }
            val["observation_type_id"] = line.observation_type_id.id or False
            val["target_min"] = line.target_min
            val["target_max"] = line.target_max
            goal_vals.append(fields.Command.create(val))
        if goal_vals:
            careplan.write({"goal_ids": goal_vals})

        for line in self.service_line_ids.filtered("selected"):
            sr_val = {
                "patient_id": careplan.patient_id.id,
                "encounter_id": careplan.encounter_id.id or False,
                "careplan_id": careplan.id,
                "period_start": careplan.period_start,
                "period_end": careplan.period_end,
                "name": line.name or "/",
                "category_id": line.category_id.id or False,
                "service_ids": [fields.Command.set(line.service_ids.ids)],
                "timing_tmpl_id": line.timing_tmpl_id.id or False,
                "intent": "plan",
            }
            self.env["ni.service.request"].create(sr_val)

        for line in self.medication_line_ids.filtered("selected"):
            if line.template_medication_id:
                med_val = line.template_medication_id.copy_data(
                    {
                        "patient_id": careplan.patient_id.id,
                        "careplan_id": careplan.id,
                        "intent": "plan",
                    }
                )[0]
                med_val["quantity"] = line.quantity
                if line.note:
                    med_val["note"] = line.note
            else:
                med_val = {
                    "patient_id": careplan.patient_id.id,
                    "careplan_id": careplan.id,
                    "name": line.medication_id.name,
                    "medication_id": line.medication_id.id,
                    "quantity": line.quantity,
                    "note": line.note or False,
                    "intent": "plan",
                }
            self.env["ni.medication.request"].create(med_val)

        selected_obs = self.obs_line_ids.filtered(
            lambda l: l.selected and l.observation_id
        ).mapped("observation_id")
        if selected_obs:
            careplan.write({"observation_ids": [fields.Command.set(selected_obs.ids)]})

        if not draft:
            careplan.action_confirm()

        return {
            "name": self.env["ni.careplan"]._description,
            "type": "ir.actions.act_window",
            "res_model": "ni.careplan",
            "view_mode": "form",
            "res_id": careplan.id,
            "views": [(False, "form")],
            "target": "new",
        }
