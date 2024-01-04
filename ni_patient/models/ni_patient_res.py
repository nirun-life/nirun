#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


class PatientResource(models.AbstractModel):
    _name = "ni.patient.res"
    _inherit = ["ni.export.data.logger"]
    _description = "Patient Resource"
    _check_company_auto = True

    """Set this param to enforce period start follow the encounter start date"""
    _check_period_start = True

    def _active_id_of(self, model: str):
        if model == self.env.context.get("active_model"):
            return self.env.context["active_id"]
        else:
            return None

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if (not fields or "encounter_id" in fields) and "encounter_id" not in res:
            if self._active_id_of("ni.encounter"):
                res["encounter_id"] = self.env.context["active_id"]
        if (not fields or "patient_id" in fields) and "patient_id" not in res:
            if self._active_id_of("ni.patient"):
                res["patient_id"] = self.env.context["active_id"]
        return res

    company_id = fields.Many2one(
        related="patient_id.company_id", store=True, readonly=True, index=True
    )
    patient_id = fields.Many2one(
        "ni.patient",
        "Patient",
        index=True,
        ondelete="cascade",
        required=True,
    )
    partner_id = fields.Many2one(related="patient_id.partner_id")
    encounter_id = fields.Many2one(
        "ni.encounter",
        "Encounter No.",
        ondelete="cascade",
        index=True,
        check_company=True,
        domain="""[
              ('patient_id', '=?', patient_id),
              ('state', 'in', ['draft','planned','in-progress'])
          ]""",
    )

    def init(self):
        if not self._abstract:
            tools.create_index(
                self._cr,
                "{}_company_id_patient_id_encounter_id_index".format(self._table),
                self._table,
                ["company_id", "patient_id", "encounter_id"],
            )

    @api.onchange("patient_id")
    def onchange_patient(self):
        if self.patient_id and (
            not self.encounter_id or self.encounter_id.patient_id != self.patient_id
        ):
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

    @api.model_create_multi
    def create(self, vals_list):
        # Because ni.patient.res may not inherit period.mixin.
        # So, we can't use @api.constraints to check this and have to manual
        # check it on create() and write()
        for vals in vals_list:
            if self._check_period_start:
                self.__check_period_start(
                    vals.get("encounter_id") or self.encounter_id.id,
                    vals.get("period_start"),
                )

            if self.env.user.has_group("base.group_multi_company"):
                # we need to explicit company_id for multi_company user to make sure
                # ni.identifier.mixin work as expected
                patient = self.env["ni.patient"].browse(vals.get("patient_id"))
                vals["company_id"] = patient.company_id.id

        return super().create(vals_list)

    def write(self, vals):
        # Because ni.patient.res may not inherit period.mixin.
        # So, we can't use @api.constraints to check this and have to manual
        # check it on create() and write()
        if self._check_period_start:
            self.__check_period_start(
                vals.get("encounter_id") or self.encounter_id.id,
                vals.get("period_start"),
            )
        return super().write(vals)

    def __check_period_start(self, encounter_id, period_start):
        if not encounter_id or not period_start:
            return

        enc = self.env["ni.encounter"].browse(encounter_id)
        start = fields.Datetime.to_datetime(period_start)
        if start.replace(microsecond=0) < enc.period_start.replace(microsecond=0):
            raise ValidationError(
                _(
                    "Since date must not before the encounter start date\n"
                    "\n\tEncounter Since: %s"
                    "\n\t%s Since: %s"
                )
                % (enc.period_start, self._description, start)
            )

    @api.constrains("patient_id", "encounter_id")
    def _check_patient_encounter(self):
        for rec in self:
            if (rec.patient_id and rec.encounter_id) and (
                rec.encounter_id.patient_id != rec.patient_id
            ):
                raise ValidationError(
                    _("Inconsistent patient and encounter references")
                )
