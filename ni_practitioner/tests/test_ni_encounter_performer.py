#  Copyright (c) 2026 NSTDA

from odoo.tests import Form

from .common import TestPractitionerCommon


class TestNiEncounterPerformer(TestPractitionerCommon):
    def test_performer_sets_licence_and_department(self):
        encounter = self._create_encounter()
        with Form(encounter) as form:
            form.performer_id = self.performer
            self.assertEqual(form.performer_license_id, self.license)
            self.assertEqual(form.performer_license_no, "Nursing license")
            self.assertEqual(form.department_id, self.department)
        self.assertEqual(encounter.performer_license_id, self.license)

    def test_changing_performer_replaces_the_licence(self):
        other = self._create_employee("Nurse Two", self.department)
        encounter = self._create_encounter()
        with Form(encounter) as form:
            form.performer_id = self.performer
            form.performer_id = other
            self.assertFalse(form.performer_license_id)
            self.assertFalse(form.performer_license_no)

    def test_other_department_clears_the_performer(self):
        ward = self.env["hr.department"].create({"name": "Other Ward"})
        encounter = self._create_encounter()
        with Form(encounter) as form:
            form.performer_id = self.performer
            form.department_id = ward
            self.assertFalse(form.performer_id)
            self.assertFalse(form.performer_license_id)
            self.assertFalse(form.performer_license_no)

    def test_licence_domain(self):
        self._create_line(self.performer, "Some course")
        domain = self.env["ni.encounter"]._fields["performer_license_id"].domain
        self.assertIsInstance(domain, str)
        self.assertIn("performer_id", domain)
        self.assertIn("identifier", domain)

    def test_create_adds_the_primary_participant(self):
        encounter = self._create_encounter(performer_id=self.performer.id)
        primary = self._primary(encounter)
        self.assertEqual(primary.employee_id, self.performer)
        self.assertFalse(primary.period_end)

    def test_write_stops_the_previous_participant(self):
        other = self._create_employee("Nurse Two", self.department)
        encounter = self._create_encounter(
            performer_id=self.performer.id, period_start="2026-01-05 02:00:00"
        )
        first = self._primary(encounter)
        encounter.performer_id = other
        self.assertTrue(first.period_end)
        active = self._primary(encounter).filtered(lambda p: not p.period_end)
        self.assertEqual(active.employee_id, other)

    def test_locked_states_are_readonly(self):
        encounter = self._create_encounter(performer_id=self.performer.id)
        for state, readonly in [("in-progress", False), ("finished", True)]:
            encounter.state = state
            form = Form(encounter)
            for name in ("performer_id", "department_id"):
                with self.subTest(state=state, field=name):
                    value = getattr(encounter, name)
                    if readonly:
                        with self.assertRaises(AssertionError):
                            setattr(form, name, value)
                    else:
                        setattr(form, name, value)

    def _primary(self, encounter):
        return encounter.participant_ids.filtered(
            lambda p: p.type_id == self.env.ref("ni_patient.PPRF")
        )
