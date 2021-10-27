#  Copyright (c) 2021 Piruin P.

from marshmallow import fields

from odoo import models

from odoo.addons.datamodel.core import Datamodel
from odoo.addons.datamodel.fields import NestedModel


class Patient(models.Model):
    _inherit = "ni.patient"

    def datamodel(self, mode=None):
        res = self.env.datamodels["ni.rest.patient"]
        if mode == "short":
            res = self.env.datamodels["ni.rest.patient.short"]

        if len(self) > 1:
            return [res(partial=True)._from(rec) for rec in self]
        else:
            return res(partial=True)._from(self)


class PatientSearchParam(Datamodel):
    _name = "ni.rest.patient.search"

    id = fields.Integer()
    name = fields.String()
    identification_id = fields.String()


class PatientShortInfo(Datamodel):
    _name = "ni.rest.patient.short"
    _inherit = "ni.rest.resource"

    id = fields.Integer(required=True)
    name = fields.String(required=True)
    company = NestedModel("ni.rest.reference", required=True)

    def _from(self, patient: Patient):
        super()._from(patient)
        self.name = patient.name
        self.company = patient.company_id.datamodel()
        return self


class PatientInfo(Datamodel):
    _name = "ni.rest.patient"
    _inherit = "ni.rest.patient.short"

    gender = fields.String()
    age = fields.Integer()
    birthdate = fields.String()
    identification_id = fields.String()
    encounter_id = fields.Integer()
    marital_status = fields.String()
    deceased = fields.Boolean()
    deceased_date = fields.String()
    nationality = NestedModel("ni.rest.coding")

    def _from(self, patient: Patient):
        super()._from(patient)

        self.gender = patient.gender
        self.age = patient.age_years
        if patient.birthdate:
            self.birthdate = patient.birthdate
        if patient.deceased:
            self.deceased = patient.deceased
            self.deceased_date = patient.deceased_date
        if patient.marital_status:
            self.marital_status = patient.marital_status
        if patient.identification_id:
            self.identification_id = patient.identification_id
        if patient.encounter_id:
            self.encounter_id = patient.encounter_id.id
        if patient.nationality_id:
            self.nationality = patient.nationality_id.datamodel()

        return self
