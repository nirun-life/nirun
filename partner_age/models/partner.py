#  Copyright (c) 2021 Piruin P.
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "res.partner"

    birthdate = fields.Date("Date of Birth", tracking=True)
    deceased_date = fields.Date("Deceased Date", tracking=True)
    deceased = fields.Boolean(
        "Deceased", compute="_compute_is_deceased", store=True, tracking=True
    )
    display_age = fields.Char(
        "Age", compute="_compute_age", compute_sudo=True, readonly=True
    )
    age = fields.Integer(
        "Age (years)",
        compute="_compute_age",
        compute_sudo=True,
        store=True,
        readonly=False,
        group_operator="avg",
        help="Deprecated field",
    )
    age_years = fields.Integer(
        "Age (years)",
        compute="_compute_age",
        compute_sudo=True,
        store=True,
        readonly=False,
        help="Deprecated field",
    )
    age_init = fields.Integer(
        "Age (Years) Input", help="Internal: Age (years) input value", readonly=True
    )
    age_init_date = fields.Date(
        "Age (Years) Input Date",
        help="Internal: Date when Age (years) input value was provided",
        readonly=True,
    )
    age_range_id = fields.Many2one(
        "res.partner.age.range",
        "Age Range",
        compute="_compute_age_range_id",
        store=True,
    )

    @api.model
    def create(self, vals):
        if vals.get("age") and not vals.get("birthdate"):
            vals.update(
                {
                    "birthdate": None,
                    "age_init": vals.get("age"),
                    "age_init_date": fields.Date.context_today(self),
                }
            )
        return super().create(vals)

    def write(self, vals):
        if vals.get("birthdate"):
            vals.update({"age_init": None, "age_init_date": None})
        elif vals.get("age"):
            vals.update(
                {
                    "birthdate": None,
                    "age_init": vals.get("age"),
                    "age_init_date": fields.Date.context_today(self),
                }
            )
        return super().write(vals)

    @api.depends("birthdate", "deceased_date", "age_init")
    def _compute_age(self):
        for rec in self:
            if rec.birthdate:
                rec._compute_age_from_birthdate()
            elif rec.age_init:
                rec._compute_age_from_init()
            else:
                rec.update({"age_years": 0, "age": 0, "display_age": None})

    def _compute_age_from_init(self):
        for rec in self:
            if rec.age_init and rec.age_init_date:
                dt = (
                    rec.deceased_date
                    if rec.deceased_date
                    else fields.Date.context_today(self)
                )
                year_diff = dt.year - rec.age_init_date.year
                year = rec.age_init + year_diff
                rec.display_age = _("%s Years") % year
                if rec.age != year:
                    # check this for reduce chance to call `_inverse_age()`
                    rec.age = year
                    rec.age_years = year

    def _compute_age_from_birthdate(self):
        for rec in self:
            if rec.birthdate:
                dt = (
                    rec.deceased_date
                    if rec.deceased_date
                    else fields.Date.context_today(self)
                )
                rd = relativedelta(dt, rec.birthdate)
                rec.display_age = self._format_age(rd)
                if rec.age != rd.years:
                    # check this for reduce chance to call `_inverse_age()`
                    rec.age = rd.years
                    rec.age_years = rd.years

    @api.model
    def _format_age(self, delta):
        result = []
        if delta.years > 0:
            result.append(_("%s Years") % delta.years)
        if delta.months > 0:
            result.append(_("%s Months") % delta.months)
        if delta.days > 0:
            result.append(_("%s Days") % delta.days)
        return " ".join(result) or None

    @api.depends("age")
    def _compute_age_range_id(self):
        range_ids = self.env["res.partner.age.range"].search([])
        for record in self:
            if not record.age:
                range_id = False
            else:
                range_id = (
                    range_ids.filtered(lambda r: r.age_from <= record.age <= r.age_to)
                    or False
                )
            if record.age_range_id != range_id:
                record.age_range_id = range_id

    @api.constrains("birthdate")
    def _check_birthdate(self):
        """ Not allow birthdates in the future. """
        for record in self:
            if not record.birthdate:
                continue
            if record.birthdate > fields.date.today():
                raise ValidationError(_("Birthdate must not be in the future",))

    @api.constrains("deceased_date")
    def _check_deceased_date(self):
        for record in self:
            if not record.deceased_date:
                continue
            if record.deceased_date > fields.date.today():
                raise ValidationError(_("Deceased date must not be in the future",))
            if record.birthdate and record.deceased_date < record.birthdate:
                raise ValidationError(_("Deceased date must not before birthdate",))

    @api.constrains("age")
    def _check_age(self):
        for rec in self:
            if rec.age < 0:
                raise ValidationError(_("Age (years) must not be less than 0"))

    @api.depends("deceased_date")
    def _compute_is_deceased(self):
        for record in self:
            record.deceased = bool(record.deceased_date)

    @api.model
    def cron_compute_age(self):
        partner = self.search(
            [
                ("deceased", "!=", True),
                "|",
                ("birthdate", "!=", False),
                ("age_init", "!=", False),
            ]
        )
        partner._compute_age()

    @api.model
    def cron_compute_age_range(self):
        partner = self.search([("age", "!=", False)])
        partner._compute_age_range_id()
