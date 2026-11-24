#  Copyright (c) 2026 NSTDA


def migrate(cr, version):
    """The view was noupdate on 16.0 and would keep its 16.0 arch"""
    cr.execute(
        """
        UPDATE ir_model_data
        SET noupdate = false
        WHERE module = 'ni_document_ref'
            AND name = 'hr_job_view_form_inherit'
            AND noupdate
        """
    )
