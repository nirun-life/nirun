#  Copyright (c) 2021 Piruin P.

from odoo import _, fields, models
from odoo.exceptions import UserError


class ActivityStateUpdate(models.TransientModel):
    _name = "ni.careplan.activity.state.wizard"
    _description = "State Update Wizard"

    activity_ids = fields.Many2many("ni.careplan.activity", store=False)
    state = fields.Selection(
        [
            ("scheduled", "Scheduled"),
            ("in-progress", "In-Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="completed",
        required=True,
    )

    def change_state(self):
        self.ensure_one()
        if not self.activity_ids:
            raise UserError(_("Please select some activity to change state!"))
        else:
            self.activity_ids.write({"state": self.state})


class Activity(models.Model):
    _inherit = "ni.careplan.activity"

    def open_state_change_wizard(self):
        ctx = dict(self.env.context)
        ctx.update({"default_activity_ids": self.ids})
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_careplan", "careplan_activity_state_wizard_action"
        )
        return dict(action, context=ctx)
