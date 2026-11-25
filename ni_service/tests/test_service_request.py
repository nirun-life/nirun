#  Copyright (c) 2026 NSTDA

from odoo.tests import Form, tagged

from .common import TestServiceCommon


@tagged("-at_install", "post_install")
class TestServiceRequest(TestServiceCommon):
    def _name(self, **context):
        return self.service_request.with_context(**context).display_name

    def test_display_name(self):
        request = self.service_request
        self.assertEqual(self._name(), "Physiotherapy Program")
        self.assertEqual(
            self._name(show_identifier=True),
            f"[{request.identifier}] Physiotherapy Program",
        )
        self.assertEqual(
            self._name(show_period=True),
            "Physiotherapy Program (2027-01-04 → 2027-03-31)",
        )
        state = dict(request._fields["state"]._description_selection(self.env))
        self.assertEqual(
            self._name(show_state=True),
            f"Physiotherapy Program [{state[request.state]}]",
        )
        request.name = "Renamed"
        self.assertEqual(self._name(), "Renamed")

    def test_service_domain(self):
        Service = self.env["ni.service"]
        routine = Service.create(
            {
                "name": "Routine",
                "category_id": self.env.ref("ni_service.categ_routine").id,
            }
        )
        child = self.env["ni.service.category"].create(
            {"name": "Child", "code": "child", "parent_id": self.category.id}
        )
        in_child = Service.create({"name": "In child", "category_id": child.id})
        other = Service.create(
            {
                "name": "Other",
                "category_id": self.env["ni.service.category"]
                .create({"name": "Other", "code": "other"})
                .id,
            }
        )
        restricted = Service.create(
            {
                "name": "Restricted",
                "category_id": self.category.id,
                "specialty_ids": [
                    (4, self.env["hr.job"].create({"name": "Therapist"}).id)
                ],
            }
        )
        services = routine | in_child | other | restricted | self.service

        request = self.service_request
        request.category_id = False
        self.assertEqual(
            services.filtered_domain(request.service_ids_domain),
            in_child | other | self.service,
        )
        request.category_id = self.category
        found = Service.search(request.service_ids_domain)
        self.assertEqual(found & services, in_child | self.service)

    def test_form(self):
        form = Form(
            self.env["ni.service.request"]
            .with_user(self.service_user)
            .with_context(
                default_patient_id=self.patient.id,
                default_encounter_id=self.encounter.id,
                default_intent="order",
            )
        )
        form.category_id = self.category
        form.service_ids.add(self.service)
        form.period_start = "2027-01-04 08:00:00"
        request = form.save()
        self.assertEqual(request.name, self.service.name)
        self.assertEqual(request.service_ids, self.service)

    def test_event_count(self):
        event = self.env["ni.service.event"].create(
            {
                "service_id": self.service.id,
                "service_ids": [(4, self.service.id)],
                "start": "2027-01-04 01:00:00",
                "stop": "2027-01-04 05:00:00",
            }
        )
        self.env["ni.encounter.service.attendance"].create(
            [
                {
                    "encounter_id": encounter.id,
                    "attendance_id": self.attendance_slot.id,
                    "service_ids": [(4, self.service.id)],
                    "service_event_id": event.id,
                }
                for encounter in (
                    self.encounter,
                    self._make_encounter("2027-01-11 08:00:00", "TEST-ENC-002"),
                )
            ]
        )
        self.assertEqual(self.service_request.event_count, 1)
        action = self.service_request.action_view_events()
        self.assertEqual(self.env["ni.service.event"].search(action["domain"]), event)
