#  Copyright (c) 2026 NSTDA

from odoo.tests import TransactionCase


class TestPractitionerCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.line_type = cls.env["hr.resume.line.type"].create({"name": "License"})
        cls.department = cls.env["hr.department"].create({"name": "Test Ward"})
        cls.performer = cls._create_employee("Nurse One", cls.department)
        cls.license = cls._create_line(cls.performer, "Nursing license", "N-0001")
        cls.patient = cls.env["ni.patient"].create(
            {
                "partner_id": cls.env["res.partner"]
                .create({"name": "Performer Test Patient"})
                .id
            }
        )

    @classmethod
    def _create_employee(cls, name, department=None):
        return cls.env["hr.employee"].create(
            {"name": name, "department_id": department.id if department else False}
        )

    @classmethod
    def _create_line(cls, employee, name, identifier=False, **vals):
        return cls.env["hr.resume.line"].create(
            {
                "employee_id": employee.id,
                "name": name,
                "identifier": identifier,
                "date_start": "2020-01-31",
                "line_type_id": cls.line_type.id,
                **vals,
            }
        )

    @classmethod
    def _create_encounter(cls, **vals):
        return cls.env["ni.encounter"].create(
            {
                "patient_id": cls.patient.id,
                "class_id": cls.env.ref("ni_patient.class_AMB").id,
                **vals,
            }
        )
