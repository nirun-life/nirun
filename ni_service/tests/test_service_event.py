#  Copyright (c) 2026 NSTDA

from freezegun import freeze_time

from odoo import fields
from odoo.tests import tagged

from .common import TestServiceCommon

EVENT_START = "2027-01-04 08:00:00"
EVENT_STOP = "2027-01-04 09:00:00"


@tagged("-at_install", "post_install")
class TestServiceEvent(TestServiceCommon):
    @freeze_time(EVENT_START)
    def test_create_service_event(self):

        event = self.env["ni.service.event"].create(
            {
                "service_id": self.service.id,
                "service_ids": [(4, self.service.id)],
                "start": fields.Datetime.from_string(EVENT_START),
                "stop": fields.Datetime.from_string(EVENT_STOP),
            }
        )

        self.assertTrue(event.event_id)
        self.assertEqual(event.name, self.service.name)
        self.assertEqual(event.service_category_ids, self.category)
