#  Copyright (c) 2025 NSTDA
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


def _my_area_depends(model):
    deps = ["city_ids"] if "city_ids" in model._fields else ["city_id"]
    deps += ["state_ids"] if "state_ids" in model._fields else ["state_id"]
    return deps


class MyAreaMixin(models.AbstractModel):
    _name = "ni.my.area.mixin"
    _description = "My Area Mixin"

    my_area = fields.Boolean(
        "พื้นที่ของฉัน", compute="_compute_my_area", search="_search_my_area"
    )

    @api.depends(_my_area_depends)
    def _compute_my_area(self):
        user = self.env.user
        is_admin = self.user_has_groups("ni_patient.group_admin")
        is_manager = self.user_has_groups("ni_patient.group_manager")
        use_city_m2m = "city_ids" in self._fields
        use_state_m2m = "state_ids" in self._fields
        for rec in self:
            if is_admin:
                rec.my_area = True
            elif is_manager:
                if use_state_m2m:
                    rec.my_area = bool(set(rec.state_ids.ids) & set(user.state_ids.ids))
                else:
                    rec.my_area = rec.state_id.id in user.state_ids.ids
            elif use_city_m2m:
                rec.my_area = bool(set(rec.city_ids.ids) & set(user.city_ids.ids))
            else:
                rec.my_area = rec.city_id.id in user.city_ids.ids

    def _search_my_area(self, operator, operand):
        if operator == "=":
            if self.user_has_groups("ni_patient.group_admin"):
                return [] if bool(operand) else [("id", "=", 0)]
            if self.user_has_groups("ni_patient.group_manager"):
                state_field = "state_ids" if "state_ids" in self._fields else "state_id"
                return [
                    (
                        state_field,
                        "in" if bool(operand) else "not in",
                        self.env.user.state_ids.ids,
                    )
                ]
            city_field = "city_ids" if "city_ids" in self._fields else "city_id"
            return [
                (
                    city_field,
                    "in" if bool(operand) else "not in",
                    self.env.user.city_ids.ids,
                )
            ]
        raise ValidationError(_("my_area support only '=', 'True' or 'False'"))
