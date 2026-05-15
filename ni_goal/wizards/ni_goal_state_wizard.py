#  Copyright (c) 2025 NSTDA
from odoo import api, fields, models


class GoalStateWizard(models.TransientModel):
    _name = "ni.goal.state.wizard"
    _description = "Goal State Wizard"

    goal_ids = fields.Many2many("ni.goal", string="Goals", required=True)
    state_id = fields.Many2one(
        "ni.goal.state", string="State", required=True, ondelete="restrict"
    )
    state_achievement_ids = fields.Many2many(related="state_id.achievement_ids")
    achievement_id = fields.Many2one(
        "ni.goal.achievement",
        ondelete="restrict",
        domain="[('id', 'in', state_achievement_ids)]",
    )
    note = fields.Html()

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "note" not in fields_list or res.get("note"):
            return res
        goal_ids = res.get("goal_ids", [])
        ids = next((cmd[2] for cmd in goal_ids if cmd[0] == 6), [])
        goals = self.env["ni.goal"].browse(ids).filtered("observation_id")
        if not goals:
            return res
        items = "".join(
            "<li>{}: {} {}</li>".format(
                g.observation_type_id.name,
                g.observation_id.value,
                g.observation_id.unit_id.name or "",
            )
            for g in goals
        )
        res["note"] = "<ul>{}</ul>".format(items)
        return res

    def action_confirm(self):
        vals = {"state_id": self.state_id.id}
        if self.achievement_id:
            vals["achievement_id"] = self.achievement_id.id
        self.goal_ids.write(vals)
        if self.note:
            for goal in self.goal_ids:
                goal.message_post(body=self.note, subtype_xmlid="mail.mt_comment")
