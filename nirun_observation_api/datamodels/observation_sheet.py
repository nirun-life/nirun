#  Copyright (c) 2021 NSTDA

from marshmallow import fields

from odoo import models

from odoo.addons.datamodel.core import Datamodel
from odoo.addons.datamodel.fields import NestedModel


class Observation(models.Model):
    _inherit = "ni.observation.sheet"

    def datamodel(self):
        ob = self.env.datamodels["ni.rest.observation.sheet"]
        rec = self[0] if len(self) > 1 else self
        return ob(partial=True)._from(rec)

    def datamodels(self):
        ob = self.env.datamodels["ni.rest.observation.sheet"]
        return [ob(partial=True)._from(rec) for rec in self]


class ObservationSearchSchema(Datamodel):
    _name = "ni.rest.observation.sheet.search"

    id = fields.Integer()
    patient_id = fields.Integer()
    limit = fields.Integer(missing=64)


class ObservationSheetSchema(Datamodel):
    _name = "ni.rest.observation.sheet"
    _inherit = "ni.rest.resource"

    identifier = fields.String()
    patient = NestedModel("ni.rest.reference", required=True)
    encounter = NestedModel("ni.rest.reference")
    effective_date = fields.DateTime(required=True)
    self_perform = fields.Boolean()
    lines = fields.List(NestedModel("ni.rest.observation.sheet.line"))
    company = NestedModel("ni.rest.reference")
    note = fields.String()

    def _from(self, rec: Observation):
        super()._from(rec)
        self.identifier = rec.name
        self.patient = rec.patient_id.datamodel()
        self.effective_date = rec.effective_date
        if rec.note:
            self.note = rec.note
        ref = self.env.datamodels["ni.rest.reference"]
        self.company = ref(id=rec.company_id.id, name=rec.company_id.name)
        if rec.encounter_id:
            self.encounter = ref(id=rec.encounter_id.id, name=rec.encounter_id.name)
        if rec.observation_ids:
            line = self.env.datamodels["ni.rest.observation.sheet.line"]
            self.lines = [line(partial=True)._from(l) for l in rec.observation_ids]

        return self


class ObservationSheetLineSchema(Datamodel):
    _name = "ni.rest.observation.sheet.line"

    id = fields.Integer()
    type = NestedModel("ni.rest.coding", require=True)
    value = fields.Float(required=True)
    interpretation = NestedModel("ni.rest.coding")
    unit = fields = NestedModel("ni.rest.coding")

    def _from(self, rec):
        self.id = rec.id
        coding = self.env.datamodels["ni.rest.coding"]
        self.type = coding(
            id=rec.type_id.id, name=rec.type_id.name, code=rec.type_id.code
        )
        self.value = rec.value
        if rec.interpretation_id:
            self.interpretation = coding(
                id=rec.interpretation_id.id,
                name=rec.interpretation_id.name,
                code=rec.interpretation_id.code,
            )
        if rec.unit:
            self.unit = coding(id=rec.unit.id, name=rec.unit.name, code=rec.unit.code)
        return self
