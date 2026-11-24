#  Copyright (c) 2023 NSTDA


def pre_init_hook(env):
    """
    Create hr_employee_category.active before the ORM does.

    Filling ``sequence`` on the existing rows searches the model
    (ni.coding ``_get_default_sequence``), and that search already filters on
    ``active``, whose column would be created later.
    """
    env.cr.execute(
        """
        ALTER TABLE IF EXISTS hr_employee_category
        ADD COLUMN IF NOT EXISTS active BOOLEAN NOT NULL DEFAULT TRUE
        """
    )
