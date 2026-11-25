#  Copyright (c) 2026 NSTDA

from importlib.util import module_from_spec, spec_from_file_location

from odoo.tests import tagged
from odoo.tools.misc import file_path

from .common import TestServiceCommon


@tagged("-at_install", "post_install")
class TestMigration(TestServiceCommon):
    def _migrate(self):
        self.env.flush_all()
        path = file_path("ni_service/migrations/17.0.1.0.0/post-migration.py")
        spec = spec_from_file_location("ni_service_post_migration", path)
        script = module_from_spec(spec)
        spec.loader.exec_module(script)
        script.migrate(self.env.cr, "16.0.0.4.3")
        self.env.invalidate_all()

    def _create_category(self, name):
        return self.env["ni.service.category"].create({"name": name, "code": name})

    def test_category_membership(self):
        other = self._create_category("Other")
        archived = self.service.copy({"name": "Archived", "active": False})
        partial = self.service.copy({"name": "Partial"})
        for service, category in (
            (self.service, False),
            (archived, False),
            (partial, other),
        ):
            service.with_context(skip_category_sync=True).category_ids = category
        self.assertEqual(partial.category, "Other")

        self._migrate()

        self.assertEqual(self.service.category_ids, self.category)
        self.assertEqual(self.service.category, self.category.name)
        self.assertEqual(archived.category_ids, self.category)
        self.assertEqual(partial.category_ids, self.category | other)
        self.assertIn(self.category.name, partial.category)

    def test_single_category_company(self):
        other = self._create_category("Other")
        service = self.service.copy({"name": "Single"})
        service.with_context(skip_category_sync=True).category_ids = other
        self.env.company.service_multi_category = False

        self._migrate()

        self.assertEqual(service.category_ids, other)
