#  Copyright (c) 2026 NSTDA


def migrate(cr, version):
    """Views and actions were noupdate on 16.0 and would keep their 16.0 arch"""
    cr.execute(
        """
        UPDATE ir_model_data
        SET noupdate = false
        WHERE module = 'ni_practitioner_role'
            AND model IN ('ir.ui.view', 'ir.actions.act_window')
            AND noupdate
        """
    )
