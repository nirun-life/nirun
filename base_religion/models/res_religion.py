#  Copyright (c) 2021 NSTDA

from odoo import _, api, fields, models


class Religion(models.Model):
    _name = "res.religion"
    _description = "Religion or Spiritual Tradition"
    _order = "name"
    _parent_store = True

    name = fields.Char(
        string="Religion Name",
        required=True,
        translate=True,
        help="The full name of the Religion.",
    )
    parent_id = fields.Many2one("res.religion", string="Major", index=True)
    parent_path = fields.Char(
        index=True, readonly=True, groups="base.group_partner_manager"
    )
    child_ids = fields.One2many(
        "res.religion", "parent_id", string="Denominations", readonly=True
    )
    active = fields.Boolean(default=True)
    _sql_constraints = [
        ("name_uniq", "unique (name)", _("Name of the religion must be unique !"))
    ]

    def name_get(self):
        if self._context.get("show_major_name"):
            result = []
            for r in self:
                name = r.name
                if r.parent_id:
                    name = "{} ({})".format(r.name, r.parent_id.name)
                result.append((r.id, name))
            return result
        return super(Religion, self).name_get()

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
