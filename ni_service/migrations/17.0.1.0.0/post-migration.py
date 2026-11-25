#  Copyright (c) 2026 NSTDA

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Make the primary category of every service one of its categories

    On 16.0 a cron, started by hand, did this for the services that are older than
    ``category_ids``.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    # a company with a single category per service keeps the one it has
    cr.execute(
        """
        INSERT INTO ni_service_category_rel (service_id, category_id)
        SELECT service.id, service.category_id
        FROM ni_service service
        JOIN res_company company ON company.id = service.company_id
        WHERE service.category_id IS NOT NULL
          AND (
            company.service_multi_category
            OR NOT EXISTS (
                SELECT 1 FROM ni_service_category_rel rel
                WHERE rel.service_id = service.id
            )
          )
        ON CONFLICT DO NOTHING
        RETURNING service_id
        """
    )
    service_ids = [row[0] for row in cr.fetchall()]
    if service_ids:
        env.invalidate_all()
        services = env["ni.service"].browse(service_ids)
        env.add_to_compute(services._fields["category"], services)
        services.flush_recordset()
