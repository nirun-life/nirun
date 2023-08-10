#  Copyright (c) 2023 NSTDA


def pre_init_hook(cr):
    """
    We need to manual alter table before odoo automate that will failre
    """
    sql = """
    ALTER TABLE IF EXISTS hr_employee_category
    ADD COLUMN IF NOT EXISTS active BOOLEAN NOT NULL DEFAULT TRUE;
    """
    cr.execute(sql)
