#  Copyright (c) 2026 NSTDA

from odoo.tests import Form, TransactionCase

from ..hooks import post_init_hook


class TestPartnerGender(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mister = cls.env.ref("partner_title.res_partner_title_mister")
        cls.madam = cls.env.ref("partner_title.res_partner_title_madam")

    def test_title_data(self):
        self.assertEqual(self.mister.gender, "male")
        self.assertEqual(self.madam.gender, "female")

    def test_onchange_title_sets_gender(self):
        with Form(self.env["res.partner"]) as form:
            form.name = "Gender Test"
            form.title_id = self.madam
            self.assertEqual(form.gender, "female")
            form.title_id = self.mister
            self.assertEqual(form.gender, "male")

    def test_onchange_title_without_gender_keeps_gender(self):
        title = self.env["res.partner.title"].create({"name": "Neutral Title"})
        with Form(self.env["res.partner"]) as form:
            form.name = "Gender Test"
            form.gender = "other"
            form.title_id = title
            self.assertEqual(form.gender, "other")

    def test_post_init_hook_backfills_gender(self):
        partner = self.env["res.partner"].create(
            {"name": "Legacy Contact", "title_id": self.mister.id, "active": False}
        )
        self.assertFalse(partner.gender)
        post_init_hook(self.env)
        self.assertEqual(partner.gender, "male")
