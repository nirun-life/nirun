#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PatientRes(models.AbstractModel):
    _name = "ni.patient.res"
    _description = "Patient Resource"
    _check_company_auto = True

    """Set this param to enforce period start follow the encounter start date"""
    _check_period_start = False

    company_id = fields.Many2one(
        related="patient_id.company_id", store=True, readonly=True, index=True
    )
    patient_id = fields.Many2one(
        "ni.patient",
        "Patient",
        store=True,
        index=True,
        ondelete="cascade",
        required=True,
    )
    partner_id = fields.Many2one(related="patient_id.partner_id")
    encounter_id = fields.Many2one(
        "ni.encounter",
        "Encounter No.",
        ondelete="restrict",
        index=True,
        check_company=True,
        domain="""[
              ('patient_id', '=?', patient_id),
              ('state', 'in', ['draft','planned','in-progress'])
          ]""",
    )

    @api.onchange("patient_id")
    def onchange_patient(self):
        if self.encounter_id.patient_id != self.patient_id:
            self.encounter_id = self.patient_id.encounter_id

        if self.patient_id.deceased:
            warning = {
                "title": _("Warning!"),
                "message": _(
                    "%s is already deceased. Reference to this patient may "
                    "cause database inconsistency!"
                )
                % self.patient_id.name,
            }
            return {"warning": warning}

    @api.onchange("encounter_id")
    def onchange_encounter(self):
        if self.encounter_id and (self.patient_id != self.encounter_id.patient_id):
            self.patient_id = self.encounter_id.patient_id

    @api.model
    def create(self, vals):
        if (
            self._check_period_start
            and vals.get("period_start")
            and vals.get("encounter_id")
        ):
            res_start = fields.Date.to_date(vals.get("period_start"))
            encounters = self.env["ni.encounter"]
            enc_start = encounters.browse(vals.get("encounter_id")).period_start
            if res_start < enc_start:
                raise ValidationError(
                    _(
                        "Since date must not before the encounter start date\n"
                        "\n\tEncounter Since: %s"
                        "\n\t%s Since: %s"
                    )
                    % (enc_start, self._description, res_start)
                )
        return super().create(vals)

    def write(self, vals):
        if (
            self._check_period_start
            and (vals.get("period_start"))
            and (vals.get("encounter_id") or self.encounter_id)
            and not ("encounter_id" in vals and not vals.get("encounter_id"))
        ):
            res_start = fields.Date.to_date(vals.get("period_start"))
            encounters = self.encounter_id or self.env["ni.encounter"].browse(
                vals.get("encounter_id")
            )
            if res_start < encounters.period_start:
                raise ValidationError(
                    _(
                        "Since date must not before the encounter start date\n"
                        "\n\tEncounter Since: %s"
                        "\n\t%s Since: %s"
                    )
                    % (encounters.period_start, self._description, res_start)
                )
        return super().write(vals)
