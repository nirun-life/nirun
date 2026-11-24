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
        cls.patient = cls.env["ni.patient"].create(
            {"partner_id": cls.env["res.partner"].create({"name": "Ada"}).id}
        )
        cls.encounter = cls.env["ni.encounter"].create(
            {
                "patient_id": cls.patient.id,
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

    def _create_draft_encounter(self, period_start):
        return self.env["ni.encounter"].create(
            {
                "patient_id": self.patient.id,
                "class_id": self.encounter.class_id.id,
                "period_start": period_start,
            }
        )

    def _create_clinician_employee(self):
        return self.env["hr.employee"].create(
            {"name": "Clinician", "user_id": self.clinician.id}
        )

    def test_confirm_adds_employee_as_participant(self):
        """Confirming an encounter adds the user's employee as participant."""
        employee = self._create_clinician_employee()
        encounter = self._create_draft_encounter(fields.Datetime.now())
        encounter.with_user(self.clinician).action_confirm()
        self.assertEqual(encounter.state, "in-progress")
        self.assertEqual(encounter.participant_ids.employee_id, employee)
        self.assertEqual(encounter.participant_ids.user_id, self.clinician)
        self.assertTrue(encounter.with_user(self.clinician).participate)

    def test_confirm_planned_does_not_add_participant_twice(self):
        """The participant added when planning is kept when the visit starts."""
        employee = self._create_clinician_employee()
        encounter = self._create_draft_encounter(
            fields.Datetime.add(fields.Datetime.now(), days=1)
        )
        encounter.with_user(self.clinician).action_confirm()
        self.assertEqual(encounter.state, "planned")
        self.assertEqual(encounter.participant_ids.employee_id, employee)
        encounter.with_user(self.clinician).action_confirm()
        self.assertEqual(encounter.state, "in-progress")
        self.assertEqual(len(encounter.participant_ids), 1)

    def test_confirm_without_employee_adds_no_participant(self):
        encounter = self._create_draft_encounter(fields.Datetime.now())
        encounter.with_user(self.clinician).action_confirm()
        self.assertEqual(encounter.state, "in-progress")
        self.assertFalse(encounter.participant_ids)
