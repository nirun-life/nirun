#  Copyright (c) 2022 Piruin P.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_goal_state = [
    ("proposed", "Proposed"),
    ("active", "Active"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
]

_term_code = {
    "short": _("STG"),
    "long": _("LTG"),
}


class Goal(models.Model):
    _name = "ni.goal"
    _description = "Goal"
    _inherit = ["ni.patient.res", "mail.thread", "mail.activity.mixin"]
    _order = "sequence"
    _rec_name = "code_id"

    sequence = fields.Integer(help="Determine the display order", index=True)
    color = fields.Integer(string="Color Index")

    code_id = fields.Many2one(
        "ni.goal.code",
        "Goal",
        required=True,
        index=True,
        tracking=True,
        ondelete="restrict",
    )
    condition_id = fields.Many2one(
        "ni.condition", ondelete="set null", help="The Problem this goal aim to solve"
    )
    description = fields.Text()
    priority = fields.Selection(
        [("1", "Low"), ("2", "Medium"), ("3", "High")],
        tracking=True,
    )
    term = fields.Selection(
        [("short", "Short Term"), ("long", "Long Term")],
        required=False,
        tracking=True,
    )
    due_date = fields.Date(tracking=True)
    achievement_id = fields.Many2one("ni.goal.achievement", tracking=True, copy=False)
    achieved = fields.Boolean(
        related="achievement_id.goal_achieved",
        string="Achieved",
        store=True,
        copy=False,
    )
    achievement_note = fields.Text("Note", trakikng=True, copy=False)
    achievement_date = fields.Datetime("Last Evaluation", readonly=True, copy=False)
    achievement_uid = fields.Many2one(
        "res.users", "Evaluated By", tracking=True, readonly=True, copy=False
    )

    state = fields.Selection(
        _goal_state,
        default="proposed",
        stored=True,
        required=False,
        tracking=True,
        readonly=False,
        copy=False,
        group_expand="_group_expand_state",
    )

    @api.onchange("achievement_id")
    def onchange_achievement_id(self):
        for rec in self:
            if rec.achievement_id.goal_state:
                rec.state = rec.achievement_id.goal_state

    @api.model
    def _group_expand_state(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    def get_state_label(self):
        self.ensure_one()
        return dict(self._fields["state"].selection).get(self.state)

    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    def _name_get(self):
        goal = self
        name = goal.code_id.name
        if self._context.get("show_term") and self.term:
            "{}: {}".format(_term_code[self.term], name)
        if self._context.get("show_patient"):
            name = "{} - {}".format(goal.patient_id._name_get(), name)
        if self._context.get("show_state"):
            name = "{} ({})".format(name, goal.get_state_label())
        return name

    def copy_data(self, default=None):
        if default is None:
            default = {}
        if "state" not in default:
            default["state"] = "proposed"
        if "activity_ids" not in default:
            default["activity_ids"] = [(5, 0, 0)]
        return super(Goal, self).copy_data(default)

    def write(self, vals):
        if "achievement_id" in vals:
            if "achievement_date" not in vals:
                vals["achievement_date"] = fields.Datetime.now()
            if "achievement_uid" not in vals:
                vals["achievement_uid"] = self.env.uid
            if "achievement_note" not in vals:
                vals["achievement_note"] = False

        return super(Goal, self).write(vals)

    def action_evaluation_wizard(self):
        action_rec = self.env.ref("nirun_goal.goal_evaluation_wizard_action")
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update({"default_goal_id": self.ids[0]})
        action["context"] = ctx
        return action

    def action_edit(self):
        self.ensure_one()
        view = {
            "name": self.code_id.name,
            "res_model": self._name,
            "type": "ir.actions.act_window",
            "target": "current",
            "res_id": self.id,
            "views": [[False, "form"]],
            "context": self.env.context,
        }
        return view

    def ensure_state(self, state: list = False):
        if not state:
            state = ["proposed"]
        goals = self.filtered_domain([("state", "not in", state)])
        if goals:
            raise ValidationError(
                _(
                    "Goals not in valid state!\n\t{} [{}]".format(
                        goals[0].name, goals[0].get_state_label()
                    )
                )
            )
        return True

    def action_cancel(self):
        self.ensure_state(["proposed", "active"])
        self.write({"state": "cancelled"})

    def action_confirm(self, force=False):
        if not force:
            self.ensure_state(["proposed"])
        self.write(
            {
                "state": "active",
                "achievement_id": self.env.ref("nirun_goal.goal_in_progress"),
                "achievement_date": None,
            }
        )
