#  Copyright (c) 2026 NSTDA


def migrate(cr, version):
    """Keep the invitation tokens: 18.0 stores company dependent fields in jsonb

    OpenUpgrade converts the fields of the core modules only. Registration links
    that were already sent have to keep working.
    """
    cr.execute("SELECT to_regclass('ir_property')")
    if not cr.fetchone()[0]:
        return
    cr.execute(
        """
        UPDATE res_users_role role
        SET access_token = property.tokens
        FROM (
            SELECT
                split_part(p.res_id, ',', 2)::int AS role_id,
                jsonb_object_agg(p.company_id::text, p.value_text) AS tokens
            FROM ir_property p
            JOIN ir_model_fields f ON f.id = p.fields_id
            WHERE f.model = 'res.users.role'
                AND f.name = 'access_token'
                AND p.res_id LIKE 'res.users.role,%'
                AND p.company_id IS NOT NULL
                AND p.value_text IS NOT NULL
            GROUP BY 1
        ) property
        WHERE role.id = property.role_id
            AND role.access_token IS NULL
        """
    )
