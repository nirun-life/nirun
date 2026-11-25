#  Copyright (c) 2026 NSTDA

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged

from .common import TestServiceCommon


@tagged("-at_install", "post_install")
class TestServiceCategories(TestServiceCommon):
    def test_service_can_belong_to_multiple_categories(self):
        self.env.company.service_multi_category = True
        second_category = self.env["ni.service.category"].create(
            {
                "name": "Rehabilitation",
                "code": "rehab",
            }
        )

        service = self.env["ni.service"].create(
            {
                "name": "Physiotherapy Combo",
                "company_id": self.env.company.id,
                "category_ids": [
                    (4, self.category.id),
                    (4, second_category.id),
                ],
                "category_id": self.category.id,
            }
        )

        self.assertCountEqual(
            service.category_ids.ids, [self.category.id, second_category.id]
        )
        self.assertIn(service.category_id, self.category | second_category)
        self.assertIn(service, self.category.service_ids)
        self.assertIn(service, second_category.service_ids)

    def test_service_rejects_multiple_categories_when_company_disables_it(self):
        second_category = self.env["ni.service.category"].create(
            {
                "name": "Rehabilitation",
                "code": "rehab",
            }
        )
        self.env.company.service_multi_category = False

        with self.assertRaises(ValidationError):
            self.env["ni.service"].create(
                {
                    "name": "Invalid Combo",
                    "company_id": self.env.company.id,
                    "category_ids": [
                        (4, self.category.id),
                        (4, second_category.id),
                    ],
                    "category_id": self.category.id,
                }
            )

    def test_category_kanban_shows_every_category(self):
        empty = self.env["ni.service.category"].create(
            {"name": "Empty", "code": "empty"}
        )
        groups = (
            self.env["ni.service.event"]
            .with_user(self.service_user)
            .with_context(read_group_expand=True)
            .web_read_group([], ["service_category_id"], ["__count"])["groups"]
        )
        ids = [g["service_category_id"][0] for g in groups if g["service_category_id"]]
        self.assertIn(empty.id, ids)
        self.assertIn(self.category.id, ids)

    def test_private_category_is_company_editable(self):
        category = (
            self.env["ni.service.category"]
            .with_user(self.service_manager)
            .create(
                {
                    "name": "Private Rehab",
                    "code": "priv-rehab",
                    "company_id": self.env.company.id,
                }
            )
        )

        category.with_user(self.service_manager).write(
            {"name": "Private Rehab Updated"}
        )

        self.assertEqual(category.name, "Private Rehab Updated")
        self.assertEqual(category.company_id, self.env.company)

    def test_private_category_takes_the_company_of_the_user(self):
        category = (
            self.env["ni.service.category"]
            .with_user(self.service_manager)
            .create({"name": "Private Rehab", "code": "priv-rehab"})
        )

        self.assertEqual(category.company_id, self.service_manager.company_id)

    def test_shared_category_requires_admin(self):
        with self.assertRaises(AccessError):
            self.env["ni.service.category"].with_user(self.service_manager).create(
                {
                    "name": "Shared Rehab",
                    "code": "shared-rehab",
                    "company_id": None,
                }
            )

        category = (
            self.env["ni.service.category"]
            .with_user(self.service_admin)
            .create(
                {
                    "name": "Shared Rehab",
                    "code": "shared-rehab",
                    "company_id": None,
                }
            )
        )
        self.assertFalse(category.company_id)

        with self.assertRaises(AccessError):
            category.with_user(self.service_manager).write({"name": "Not Allowed"})

        category.with_user(self.service_admin).write({"name": "Shared Rehab Updated"})
        self.assertEqual(category.name, "Shared Rehab Updated")

    def test_private_type_is_company_editable(self):
        service_type = (
            self.env["ni.service.type"]
            .with_user(self.service_manager)
            .create(
                {
                    "name": "Private Type",
                    "code": "priv-type",
                    "company_id": self.env.company.id,
                }
            )
        )

        service_type.with_user(self.service_manager).write(
            {"name": "Private Type Updated"}
        )

        self.assertEqual(service_type.name, "Private Type Updated")
        self.assertEqual(service_type.company_id, self.env.company)

    def test_shared_type_requires_admin(self):
        with self.assertRaises(AccessError):
            self.env["ni.service.type"].with_user(self.service_manager).create(
                {
                    "name": "Shared Type",
                    "code": "shared-type",
                    "company_id": None,
                }
            )

        service_type = (
            self.env["ni.service.type"]
            .with_user(self.service_admin)
            .create(
                {
                    "name": "Shared Type",
                    "code": "shared-type",
                    "company_id": None,
                }
            )
        )
        self.assertFalse(service_type.company_id)

        with self.assertRaises(AccessError):
            service_type.with_user(self.service_manager).write({"name": "Not Allowed"})

        service_type.with_user(self.service_admin).write(
            {"name": "Shared Type Updated"}
        )
        self.assertEqual(service_type.name, "Shared Type Updated")
