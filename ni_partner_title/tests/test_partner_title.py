#  Copyright (c) 2026 NSTDA

from odoo.tests import Form, common


class TestPartnerTitle(common.TransactionCase):
    def test_default_titles(self):
        for xmlid in ("madam", "miss", "mister", "doctor", "prof"):
            self.assertTrue(self.env.ref(f"ni_partner_title.res_partner_title_{xmlid}"))

    def test_partner_title(self):
        mister = self.env.ref("ni_partner_title.res_partner_title_mister")
        with Form(self.env["res.partner"]) as form:
            form.name = "Title Test"
            form.title_id = mister
        self.assertEqual(form.record.title_id, mister)
