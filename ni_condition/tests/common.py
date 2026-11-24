#  Copyright (c) 2026 NSTDA
from odoo import fields
from odoo.tests.common import TransactionCase


class ConditionCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls._create_patient("Condition Test Patient")
        cls.system = cls.env.ref("ni_coding.system_internal")
        cls.code_a = cls._create_code("Alpha Disease", "T-ALPHA", "AD")
        cls.code_b = cls._create_code("Beta Disease", "T-BETA")
        cls.role_chief = cls.env.ref("ni_condition.encounter_dx_role_cc")
        cls.role_other = cls.env["ni.encounter.diagnosis.role"].create(
            {"name": "Test Role", "code": "T-ROLE", "system_id": cls.system.id}
        )

    @classmethod
    def _create_patient(cls, name):
        partner = cls.env["res.partner"].create({"name": name})
        return cls.env["ni.patient"].create({"partner_id": partner.id})

    @classmethod
    def _create_code(cls, name, code, abbr=False, **vals):
        return cls.env["ni.condition.code"].create(
            {
                "name": name,
                "code": code,
                "abbr": abbr,
                "system_id": cls.system.id,
                **vals,
            }
        )

    @classmethod
    def _create_encounter(cls, patient=None):
        return cls.env["ni.encounter"].create(
            {
                "patient_id": (patient or cls.patient).id,
                "class_id": cls.env.ref("ni_patient.class_IMP").id,
                "period_start": fields.Datetime.now(),
            }
        )

    @classmethod
    def _create_condition(cls, code=None, **vals):
        return cls.env["ni.condition"].create(
            {
                "patient_id": cls.patient.id,
                "name": code.name if code else "Free text",
                "code_id": code.id if code else False,
                **vals,
            }
        )

    @classmethod
    def _create_diagnosis(cls, encounter, code, role, **vals):
        return cls.env["ni.encounter.diagnosis"].create(
            {
                "encounter_id": encounter.id,
                "patient_id": encounter.patient_id.id,
                "name": code.name,
                "code_id": code.id,
                "role_id": role.id,
                "is_diagnosis": True,
                **vals,
            }
        )
