#  Copyright (c) 2026 NSTDA

from odoo import fields
from odoo.tests.common import TransactionCase, new_test_user


class TestEncounterParticipant(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.clinician = new_test_user(
            cls.env,
            login="encounter.clinician",
            groups="base.group_user,ni_patient.group_user",
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Practitioner",
                "job_title": "Registered Nurse",
                "permit_no": "RN-0001",
            }
        )
        patient = cls.env["ni.patient"].create(
            {"partner_id": cls.env["res.partner"].create({"name": "Ada"}).id}
        )
        cls.encounter = cls.env["ni.encounter"].create(
            {
                "patient_id": patient.id,
                "class_id": cls.env["ni.encounter.class"].search([], limit=1).id,
                "participant_ids": [
                    (
                        0,
                        0,
                        {
                            "employee_id": cls.employee.id,
                            "period_start": fields.Datetime.now(),
                        },
                    )
                ],
            }
        )

    def test_non_hr_user_reads_participant(self):
        """A clinician without HR rights can open the encounter and sees the
        practitioner's job title and permit number."""
        # Nothing cached from the setup, as when the clinician opens the form.
        self.env.invalidate_all()
        encounter = self.encounter.with_user(self.clinician)
        values = encounter.read(
            ["participant_id", "participant_title", "participant_permit_no"]
        )[0]
        self.assertEqual(values["participant_id"][0], encounter.participant_ids.id)
        self.assertEqual(values["participant_title"], "Registered Nurse")
        self.assertEqual(values["participant_permit_no"], "RN-0001")
