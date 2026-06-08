#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestFlagViews(common.TransactionCase):
    def test_encounter_flag_view_inherits_are_valid(self):
        views = [
            "ni_flag.ni_encounter_view_form_inherit",
            "ni_flag.ni_encounter_view_tree_inherit",
            "ni_flag.ni_encounter_view_kanban_inherit",
            "ni_flag.ni_encounter_view_search_inherit",
            "ni_flag.ni_flag_view_kanban",
        ]
        for xmlid in views:
            view = self.env.ref(xmlid)
            self.assertTrue(view.arch_db)

    def test_flag_report_actions_exist(self):
        actions = [
            "ni_flag.ni_flag_action",
            "ni_flag.ni_patient_flag_action",
            "ni_flag.ni_encounter_flag_action",
            "ni_flag.ni_flag_recommendation_action",
        ]
        for xmlid in actions:
            action = self.env.ref(xmlid)
            self.assertTrue(action.name)

    def test_patient_manage_flags_server_action_binding(self):
        action = self.env.ref("ni_flag.ni_patient_action_manage_flags")
        self.assertEqual(action.model_id.model, "ni.patient")
        self.assertEqual(action.binding_model_id.model, "ni.patient")
        self.assertEqual(action.binding_view_types, "form")
        self.assertEqual(action.state, "code")

    def test_encounter_manage_flags_server_action_binding(self):
        action = self.env.ref("ni_flag.ni_encounter_action_manage_flags")
        self.assertEqual(action.model_id.model, "ni.encounter")
        self.assertEqual(action.binding_model_id.model, "ni.encounter")
        self.assertEqual(action.binding_view_types, "form")
        self.assertEqual(action.state, "code")

    def test_flag_search_view_supports_group_by_state(self):
        view = self.env.ref("ni_flag.ni_flag_view_search")
        self.assertIn("group_state", view.arch_db)
        self.assertIn("'group_by': 'status'", view.arch_db)

    def test_flag_kanban_view_has_status_progressbar(self):
        view = self.env.ref("ni_flag.ni_flag_view_kanban")
        self.assertIn("progressbar", view.arch_db)
        self.assertIn('field="status"', view.arch_db)
        self.assertIn("&quot;active&quot;: &quot;success&quot;", view.arch_db)
        self.assertIn("&quot;inactive&quot;: &quot;warning&quot;", view.arch_db)
        self.assertIn("&quot;entered-in-error&quot;: &quot;danger&quot;", view.arch_db)
