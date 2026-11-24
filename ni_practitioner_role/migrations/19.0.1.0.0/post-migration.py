#  Copyright (c) 2026 NSTDA


def migrate(cr, version):
    """Keep the role colors: res.groups.color is gone in 19.0"""
    cr.execute(
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'res_groups' AND column_name = 'color'
        """
    )
    if not cr.fetchone():
        return
    cr.execute(
        """
        UPDATE res_users_role role
        SET color = groups.color
        FROM res_groups groups
        WHERE groups.id = role.group_id AND groups.color IS NOT NULL
        """
    )
