#  Copyright (c) 2026 NSTDA

from lxml import etree

from odoo.tests import TransactionCase


class TestNoChatter(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "No chatter"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})
        cls.encounter = cls.env["ni.encounter"].create(
            {
                "patient_id": cls.patient.id,
                "class_id": cls.env.ref("ni_patient.class_AMB").id,
            }
        )

    def test_server_action_toggles(self):
        for record, xmlid in (
            (self.patient, "ni_patient_no_chatter.ni_patient_action_no_chatter"),
            (self.encounter, "ni_patient_no_chatter.ni_encounter_action_no_chatter"),
        ):
            server_action = self.env.ref(xmlid)
            ctx = {"active_model": record._name, "active_ids": record.ids}
            action = server_action.with_context(**ctx).run()
            self.assertEqual(action["res_model"], record._name)
            self.assertEqual(action["res_id"], record.id)
            self.assertEqual(action["views"], [[False, "form"]])
            # hidden by default: the first toggle shows the chatter
            self.assertIs(action["context"]["no_chatter"], False)
            action = server_action.with_context(**ctx, no_chatter=False).run()
            self.assertIs(action["context"]["no_chatter"], True)

    def test_chatter_follows_the_context(self):
        for model in ("ni.patient", "ni.encounter"):
            arch = etree.fromstring(self.env[model].get_view(view_type="form")["arch"])
            chatter = arch.xpath("//div[@name='chatter']")
            self.assertEqual(len(chatter), 1, model)
            self.assertEqual(
                chatter[0].get("invisible"), "context.get('no_chatter', True)"
            )
