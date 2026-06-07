# NI Flag PR95 Improvement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve PR #95 by making encounter flag UX easier to scan, adding flag reports, and introducing recommendation-first
observation-driven flagging with evidence and conflict handling.

**Architecture:** Keep `ni.flag` as the durable FHIR Flag record. Add rule and recommendation models that evaluate observations
and either create pending recommendations or, for admin-approved rules only, auto-apply flags. Store the source observation on
accepted/auto-created flags so the flag detail always shows why it exists.

**Tech Stack:** Odoo 16.0 add-on module `ni_flag`, Python 3.10 ORM models, XML views/actions/security,
`odoo.tests.TransactionCase`.

---

## Current PR Context

PR #95 adds `ni_flag` with:

- `ni.flag`, `ni.flag.code`, and `ni.flag.category`
- inline editable flag tags on patient and encounter forms
- active flag tags on patient kanban
- flag tree, pivot, graph, and configuration menus
- unit tests for patient-level and encounter-scoped tag compute/inverse behavior

The improvement work should be implemented on branch `16.0-feat-ni_flag`.

## File Structure

Modify existing PR files:

- `ni_flag/__manifest__.py`: add new data, security, and view XML files.
- `ni_flag/models/__init__.py`: import new rule, recommendation, wizard-support models.
- `ni_flag/models/ni_flag.py`: add evidence, origin, conflict helpers, and action buttons.
- `ni_flag/models/ni_flag_code.py`: add conflict metadata and rule/report helpers.
- `ni_flag/models/ni_patient.py`: add recommendation counts/actions if patient-level smart access is desired.
- `ni_flag/models/ni_encounter.py`: add encounter UX helper fields/actions.
- `ni_flag/views/ni_flag_views.xml`: show evidence observation and source recommendation on flag detail.
- `ni_flag/views/ni_flag_code_views.xml`: configure conflicts on flag codes.
- `ni_flag/views/ni_patient_views.xml`: add recommendation indicators if needed.
- `ni_flag/views/ni_encounter_views.xml`: improve form, kanban, tree, and search flag UX.
- `ni_flag/views/ni_flag_menu.xml`: add report and recommendation menus.
- `ni_flag/tests/test_flag.py`: extend existing flag inverse/conflict/evidence tests.

Create new files:

- `ni_flag/models/ni_flag_recommendation_rule.py`: rule model that maps observations to flag recommendations.
- `ni_flag/models/ni_flag_recommendation.py`: pending/accepted/dismissed/auto-applied recommendation model.
- `ni_flag/models/ni_observation.py`: inherit `ni.observation` and trigger recommendation evaluation after observation value
  changes.
- `ni_flag/wizards/__init__.py`: import conflict wizard.
- `ni_flag/wizards/ni_flag_conflict_wizard.py`: confirmation wizard for conflicting manual/recommended flags.
- `ni_flag/security/ir.model.access.csv`: add access for rules, recommendations, and wizard.
- `ni_flag/security/ni_flag_security.xml`: add record rules for recommendations and admin-only rule writes.
- `ni_flag/views/ni_flag_recommendation_rule_views.xml`: admin rule configuration views.
- `ni_flag/views/ni_flag_recommendation_views.xml`: recommendation review views and actions.
- `ni_flag/views/ni_flag_conflict_wizard_views.xml`: conflict confirmation modal.
- `ni_flag/tests/test_flag_recommendation.py`: rule evaluation and evidence tests.
- `ni_flag/tests/test_flag_conflict.py`: conflict replacement tests.
- `ni_flag/tests/test_flag_views.py`: view inheritance smoke tests.

---

### Task 1: Prepare PR Branch and Baseline Checks

**Files:**

- Read: `ni_flag/__manifest__.py`
- Read: `ni_flag/models/ni_flag.py`
- Read: `ni_flag/models/ni_patient.py`
- Read: `ni_flag/models/ni_encounter.py`
- Read: `ni_flag/tests/test_flag.py`

- [ ] **Step 1: Switch to the PR branch**

Run:

```bash
git checkout 16.0-feat-ni_flag
git pull --ff-only origin 16.0-feat-ni_flag
```

Expected: working tree on `16.0-feat-ni_flag` with PR #95 changes present.

- [ ] **Step 2: Confirm branch files exist**

Run:

```bash
test -f ni_flag/models/ni_flag.py && test -f ni_flag/views/ni_encounter_views.xml && test -f ni_flag/tests/test_flag.py
```

Expected: command exits with status `0`.

- [ ] **Step 3: Run existing module tests**

Run with the local Odoo binary configured in `ODOO_BIN`:

```bash
$ODOO_BIN -c odoo.conf -i ni_flag --test-enable --stop-after-init
```

Expected: existing `ni_flag` tests pass before new changes are made.

---

### Task 2: Add Flag Evidence and Origin Fields

**Files:**

- Modify: `ni_flag/models/ni_flag.py`
- Modify: `ni_flag/views/ni_flag_views.xml`
- Test: `ni_flag/tests/test_flag.py`

- [ ] **Step 1: Write failing tests for observation evidence on a flag**

Add these tests to `ni_flag/tests/test_flag.py`:

```python
def test_flag_can_store_source_observation(self):
    obs_type = self.env["ni.observation.type"].create(
        {"name": "Flag Evidence Test", "code": "FLAG-EVIDENCE", "value_type": "float"}
    )
    observation = self.env["ni.observation"].create(
        {
            "patient_id": self.patient.id,
            "encounter_id": self.encounter.id,
            "type_id": obs_type.id,
            "value_float": 9.0,
        }
    )
    flag = self.env["ni.flag"].create(
        {
            "patient_id": self.patient.id,
            "encounter_id": self.encounter.id,
            "code_id": self.code_fall.id,
            "source_observation_id": observation.id,
            "origin": "recommendation",
        }
    )
    self.assertEqual(flag.source_observation_id, observation)
    self.assertEqual(flag.origin, "recommendation")

def test_manual_flag_origin_defaults_to_manual(self):
    flag = self._make_flag(self.code_dnr)
    self.assertEqual(flag.origin, "manual")
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
$ODOO_BIN -c odoo.conf -i ni_flag --test-enable --stop-after-init
```

Expected: failures mention missing `source_observation_id` and `origin`.

- [ ] **Step 3: Add evidence and origin fields**

In `ni_flag/models/ni_flag.py`, add fields inside `class Flag(models.Model):`

```python
origin = fields.Selection(
    [
        ("manual", "Manual"),
        ("recommendation", "Recommendation"),
        ("auto_rule", "Auto Rule"),
    ],
    default="manual",
    required=True,
    index=True,
)
source_observation_id = fields.Many2one(
    "ni.observation",
    "Source Observation",
    ondelete="set null",
    index=True,
    help="Observation that caused this flag to be recommended or created.",
)
recommendation_id = fields.Many2one(
    "ni.flag.recommendation",
    "Source Recommendation",
    ondelete="set null",
    index=True,
)
evidence_summary = fields.Char(compute="_compute_evidence_summary")
```

Add the compute method:

```python
@api.depends(
    "origin",
    "source_observation_id",
    "source_observation_id.type_id",
    "source_observation_id.value",
    "source_observation_id.interpretation_id",
)
def _compute_evidence_summary(self):
    for rec in self:
        observation = rec.source_observation_id
        if not observation:
            rec.evidence_summary = rec.origin
            continue
        parts = [
            observation.type_id.display_name or observation.type_id.name,
            observation.value or "",
            observation.interpretation_id.display_name
            or observation.interpretation_id.name
            or "",
        ]
        rec.evidence_summary = " / ".join([part for part in parts if part])
```

- [ ] **Step 4: Add evidence to the flag detail form**

In `ni_flag/views/ni_flag_views.xml`, add an Evidence page in the flag form notebook:

```xml
<page name="evidence" string="Evidence">
    <group>
        <field name="origin" readonly="1" />
        <field name="source_observation_id" readonly="1" options="{'no_create': True}" />
        <field name="recommendation_id" readonly="1" options="{'no_create': True}" />
        <field name="evidence_summary" readonly="1" />
    </group>
</page>
```

- [ ] **Step 5: Run tests**

Run:

```bash
$ODOO_BIN -c odoo.conf -i ni_flag --test-enable --stop-after-init
```

Expected: evidence tests pass.

- [ ] **Step 6: Commit**

```bash
git add ni_flag/models/ni_flag.py ni_flag/views/ni_flag_views.xml ni_flag/tests/test_flag.py
git commit -m "[IMP] ni_flag: add flag evidence origin"
```

---

### Task 3: Add Recommendation Rule Model

**Files:**

- Create: `ni_flag/models/ni_flag_recommendation_rule.py`
- Modify: `ni_flag/models/__init__.py`
- Modify: `ni_flag/security/ir.model.access.csv`
- Create: `ni_flag/views/ni_flag_recommendation_rule_views.xml`
- Modify: `ni_flag/views/ni_flag_menu.xml`
- Modify: `ni_flag/__manifest__.py`
- Test: `ni_flag/tests/test_flag_recommendation.py`

- [ ] **Step 1: Write failing tests for rule matching**

Create `ni_flag/tests/test_flag_recommendation.py`:

```python
#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestFlagRecommendation(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "Recommendation Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})
        cls.encounter = cls.env["ni.encounter"].create(
            {
                "patient_id": cls.patient.id,
                "class_id": cls.env.ref("ni_patient.class_AMB").id,
            }
        )
        cls.flag_code = cls.env.ref("ni_flag.code_fall")
        cls.obs_type = cls.env["ni.observation.type"].create(
            {"name": "Fall Score", "code": "FALL-SCORE", "value_type": "float"}
        )
        cls.interpretation = cls.env["ni.observation.interpretation"].create(
            {
                "name": "High Risk",
                "code": "HIGH-RISK",
                "display_class": "danger",
                "is_problem": True,
            }
        )

    def test_rule_matches_observation_interpretation(self):
        rule = self.env["ni.flag.recommendation.rule"].create(
            {
                "name": "High fall score recommends fall risk",
                "observation_type_id": self.obs_type.id,
                "interpretation_id": self.interpretation.id,
                "flag_code_id": self.flag_code.id,
                "scope": "encounter",
                "mode": "recommend",
            }
        )
        observation = self.env["ni.observation"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "type_id": self.obs_type.id,
                "value_float": 12.0,
                "interpretation_id": self.interpretation.id,
            }
        )
        self.assertTrue(rule._matches_observation(observation))
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
$ODOO_BIN -c odoo.conf -i ni_flag --test-enable --stop-after-init
```

Expected: failure mentions missing `ni.flag.recommendation.rule`.

- [ ] **Step 3: Implement rule model**

Create `ni_flag/models/ni_flag_recommendation_rule.py`:

```python
#  Copyright (c) 2026 NSTDA

from odoo import fields, models


class FlagRecommendationRule(models.Model):
    _name = "ni.flag.recommendation.rule"
    _description = "Flag Recommendation Rule"
    _order = "sequence, name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    observation_type_id = fields.Many2one(
        "ni.observation.type", required=True, ondelete="cascade", index=True
    )
    interpretation_id = fields.Many2one(
        "ni.observation.interpretation",
        ondelete="restrict",
        help="Match when the observation has this interpretation.",
    )
    value_code_id = fields.Many2one(
        "ni.observation.value.code",
        ondelete="restrict",
        help="Match when a single-choice observation has this value code.",
    )
    value_code_ids = fields.Many2many(
        "ni.observation.value.code",
        "ni_flag_rule_value_code_rel",
        "rule_id",
        "value_code_id",
        help="Match when a multi-choice observation includes any of these values.",
    )
    flag_code_id = fields.Many2one("ni.flag.code", required=True, ondelete="restrict")
    scope = fields.Selection(
        [("patient", "Patient"), ("encounter", "Encounter")],
        default="encounter",
        required=True,
    )
    mode = fields.Selection(
        [("recommend", "Recommend"), ("auto_apply", "Auto Apply")],
        default="recommend",
        required=True,
    )
    note = fields.Text()

    def _matches_observation(self, observation):
        self.ensure_one()
        if not self.active or observation.type_id != self.observation_type_id:
            return False
        if self.interpretation_id and observation.interpretation_id != self.interpretation_id:
            return False
        if self.value_code_id and observation.value_code_id != self.value_code_id:
            return False
        if self.value_code_ids and not (observation.value_code_ids & self.value_code_ids):
            return False
        return True
```

- [ ] **Step 4: Import rule model**

In `ni_flag/models/__init__.py`, add:

```python
from . import ni_flag_recommendation_rule
```

- [ ] **Step 5: Add access rights**

Append to `ni_flag/security/ir.model.access.csv`:

```csv
access_ni_flag_recommendation_rule_user,access_ni_flag_recommendation_rule_user,model_ni_flag_recommendation_rule,ni_patient.group_user,1,0,0,0
access_ni_flag_recommendation_rule_admin,access_ni_flag_recommendation_rule_admin,model_ni_flag_recommendation_rule,ni_patient.group_admin,1,1,1,1
```

- [ ] **Step 6: Add rule views**

Create `ni_flag/views/ni_flag_recommendation_rule_views.xml`:

```xml
<?xml version="1.0" encoding="utf-8" ?>
<odoo>
    <record id="ni_flag_recommendation_rule_view_tree" model="ir.ui.view">
        <field name="name">ni.flag.recommendation.rule.view.tree</field>
        <field name="model">ni.flag.recommendation.rule</field>
        <field name="arch" type="xml">
            <tree>
                <field name="sequence" widget="handle" />
                <field name="name" />
                <field name="observation_type_id" />
                <field name="interpretation_id" optional="show" />
                <field name="value_code_id" optional="hide" />
                <field name="flag_code_id" />
                <field name="scope" widget="badge" />
                <field name="mode" widget="badge" decoration-warning="mode == 'auto_apply'" />
                <field name="active" widget="boolean_toggle" />
            </tree>
        </field>
    </record>
    <record id="ni_flag_recommendation_rule_view_form" model="ir.ui.view">
        <field name="name">ni.flag.recommendation.rule.view.form</field>
        <field name="model">ni.flag.recommendation.rule</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <group>
                        <group>
                            <field name="name" />
                            <field name="active" />
                            <field name="sequence" />
                            <field name="observation_type_id" />
                        </group>
                        <group>
                            <field name="flag_code_id" />
                            <field name="scope" />
                            <field name="mode" />
                        </group>
                    </group>
                    <group string="Match Conditions">
                        <field name="interpretation_id" />
                        <field name="value_code_id" />
                        <field name="value_code_ids" widget="many2many_tags" />
                    </group>
                    <field name="note" placeholder="Clinical rationale for this rule..." />
                </sheet>
            </form>
        </field>
    </record>
    <record id="ni_flag_recommendation_rule_action" model="ir.actions.act_window">
        <field name="name">Flag Recommendation Rules</field>
        <field name="res_model">ni.flag.recommendation.rule</field>
        <field name="view_mode">tree,form</field>
    </record>
</odoo>
```

- [ ] **Step 7: Add rule menu and manifest entries**

In `ni_flag/views/ni_flag_menu.xml`, under the flag configuration menu, add:

```xml
<menuitem
    id="ni_flag_recommendation_rule_menu"
    name="Recommendation Rules"
    parent="ni_flag_config_menu"
    action="ni_flag_recommendation_rule_action"
    sequence="40"
    groups="ni_patient.group_admin"
/>
```

In `ni_flag/__manifest__.py`, add the view file after flag code/category views:

```python
"views/ni_flag_recommendation_rule_views.xml",
```

- [ ] **Step 8: Run tests**

Run:

```bash
$ODOO_BIN -c odoo.conf -i ni_flag --test-enable --stop-after-init
```

Expected: rule matching test passes.

- [ ] **Step 9: Commit**

```bash
git add ni_flag/models ni_flag/security/ir.model.access.csv ni_flag/views ni_flag/__manifest__.py ni_flag/tests/test_flag_recommendation.py
git commit -m "[IMP] ni_flag: add recommendation rules"
```

---

### Task 4: Add Recommendation Records and Observation Trigger

**Files:**

- Create: `ni_flag/models/ni_flag_recommendation.py`
- Create: `ni_flag/models/ni_observation.py`
- Modify: `ni_flag/models/__init__.py`
- Modify: `ni_flag/security/ir.model.access.csv`
- Create: `ni_flag/views/ni_flag_recommendation_views.xml`
- Modify: `ni_flag/views/ni_flag_menu.xml`
- Modify: `ni_flag/__manifest__.py`
- Test: `ni_flag/tests/test_flag_recommendation.py`

- [ ] **Step 1: Add failing tests for recommendation-first behavior**

Append to `ni_flag/tests/test_flag_recommendation.py`:

```python
def test_observation_creates_pending_recommendation(self):
    self.env["ni.flag.recommendation.rule"].create(
        {
            "name": "High fall score recommends fall risk",
            "observation_type_id": self.obs_type.id,
            "interpretation_id": self.interpretation.id,
            "flag_code_id": self.flag_code.id,
            "scope": "encounter",
            "mode": "recommend",
        }
    )
    observation = self.env["ni.observation"].create(
        {
            "patient_id": self.patient.id,
            "encounter_id": self.encounter.id,
            "type_id": self.obs_type.id,
            "value_float": 12.0,
            "interpretation_id": self.interpretation.id,
        }
    )
    recommendation = self.env["ni.flag.recommendation"].search(
        [("source_observation_id", "=", observation.id)]
    )
    self.assertEqual(len(recommendation), 1)
    self.assertEqual(recommendation.state, "pending")
    self.assertEqual(recommendation.flag_code_id, self.flag_code)
    self.assertFalse(
        self.env["ni.flag"].search(
            [("source_observation_id", "=", observation.id), ("status", "=", "active")]
        )
    )

def test_auto_apply_rule_creates_flag_with_evidence(self):
    self.env["ni.flag.recommendation.rule"].create(
        {
            "name": "Auto high fall score",
            "observation_type_id": self.obs_type.id,
            "interpretation_id": self.interpretation.id,
            "flag_code_id": self.flag_code.id,
            "scope": "encounter",
            "mode": "auto_apply",
        }
    )
    observation = self.env["ni.observation"].create(
        {
            "patient_id": self.patient.id,
            "encounter_id": self.encounter.id,
            "type_id": self.obs_type.id,
            "value_float": 12.0,
            "interpretation_id": self.interpretation.id,
        }
    )
    flag = self.env["ni.flag"].search(
        [("source_observation_id", "=", observation.id), ("status", "=", "active")]
    )
    self.assertEqual(len(flag), 1)
    self.assertEqual(flag.origin, "auto_rule")
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
$ODOO_BIN -c odoo.conf -i ni_flag --test-enable --stop-after-init
```

Expected: failure mentions missing `ni.flag.recommendation` and trigger behavior.

- [ ] **Step 3: Implement recommendation model**

Create `ni_flag/models/ni_flag_recommendation.py`:

```python
#  Copyright (c) 2026 NSTDA

from odoo import fields, models


class FlagRecommendation(models.Model):
    _name = "ni.flag.recommendation"
    _description = "Flag Recommendation"
    _order = "create_date DESC, id DESC"

    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("dismissed", "Dismissed"),
            ("auto_applied", "Auto Applied"),
        ],
        default="pending",
        required=True,
        index=True,
    )
    patient_id = fields.Many2one("ni.patient", required=True, index=True)
    encounter_id = fields.Many2one("ni.encounter", index=True)
    rule_id = fields.Many2one("ni.flag.recommendation.rule", required=True, index=True)
    flag_code_id = fields.Many2one("ni.flag.code", required=True, ondelete="restrict")
    source_observation_id = fields.Many2one(
        "ni.observation", required=True, ondelete="cascade", index=True
    )
    flag_id = fields.Many2one("ni.flag", ondelete="set null", index=True)
    reason = fields.Char(compute="_compute_reason", store=True)
    note = fields.Text()

    def _flag_values(self, origin):
        self.ensure_one()
        values = {
            "patient_id": self.patient_id.id,
            "code_id": self.flag_code_id.id,
            "origin": origin,
            "source_observation_id": self.source_observation_id.id,
            "recommendation_id": self.id,
        }
        if self.encounter_id:
            values["encounter_id"] = self.encounter_id.id
        return values

    def action_accept(self):
        Flag = self.env["ni.flag"]
        for rec in self.filtered(lambda r: r.state == "pending"):
            flag = Flag.create(rec._flag_values("recommendation"))
            rec.write({"state": "accepted", "flag_id": flag.id})

    def action_dismiss(self):
        self.filtered(lambda r: r.state == "pending").write({"state": "dismissed"})

    def action_auto_apply(self):
        Flag = self.env["ni.flag"]
        for rec in self.filtered(lambda r: r.state == "pending"):
            flag = Flag.create(rec._flag_values("auto_rule"))
            rec.write({"state": "auto_applied", "flag_id": flag.id})
```

Add the reason compute:

```python
from odoo import api, fields, models

@api.depends(
    "source_observation_id.type_id",
    "source_observation_id.value",
    "source_observation_id.interpretation_id",
    "flag_code_id",
)
def _compute_reason(self):
    for rec in self:
        observation = rec.source_observation_id
        rec.reason = "%s %s recommends %s" % (
            observation.type_id.display_name or observation.type_id.name,
            observation.value or "",
            rec.flag_code_id.display_name or rec.flag_code_id.name,
        )
```

- [ ] **Step 4: Implement observation trigger**

Create `ni_flag/models/ni_observation.py`:

```python
#  Copyright (c) 2026 NSTDA

from odoo import api, models


class Observation(models.Model):
    _inherit = "ni.observation"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._evaluate_flag_recommendations()
        return records

    def write(self, vals):
        result = super().write(vals)
        watched = {
            "type_id",
            "value",
            "value_float",
            "value_int",
            "value_char",
            "value_code_id",
            "value_code_ids",
            "interpretation_id",
            "patient_id",
            "encounter_id",
        }
        if result and watched.intersection(vals):
            self._evaluate_flag_recommendations()
        return result

    def _evaluate_flag_recommendations(self):
        Recommendation = self.env["ni.flag.recommendation"]
        Rule = self.env["ni.flag.recommendation.rule"]
        for observation in self.filtered(lambda r: r.patient_id and r.type_id):
            rules = Rule.search(
                [
                    ("active", "=", True),
                    ("observation_type_id", "=", observation.type_id.id),
                ]
            )
            for rule in rules.filtered(lambda r: r._matches_observation(observation)):
                existing = Recommendation.search(
                    [
                        ("source_observation_id", "=", observation.id),
                        ("rule_id", "=", rule.id),
                        ("state", "in", ["pending", "accepted", "auto_applied"]),
                    ],
                    limit=1,
                )
                if existing:
                    continue
                recommendation = Recommendation.create(
                    {
                        "patient_id": observation.patient_id.id,
                        "encounter_id": observation.encounter_id.id
                        if rule.scope == "encounter"
                        else False,
                        "rule_id": rule.id,
                        "flag_code_id": rule.flag_code_id.id,
                        "source_observation_id": observation.id,
                    }
                )
                if rule.mode == "auto_apply":
                    recommendation.action_auto_apply()
```

- [ ] **Step 5: Import models**

In `ni_flag/models/__init__.py`, add:

```python
from . import ni_flag_recommendation
from . import ni_observation
```

- [ ] **Step 6: Add access rights**

Append to `ni_flag/security/ir.model.access.csv`:

```csv
access_ni_flag_recommendation_user,access_ni_flag_recommendation_user,model_ni_flag_recommendation,ni_patient.group_user,1,1,1,0
access_ni_flag_recommendation_admin,access_ni_flag_recommendation_admin,model_ni_flag_recommendation,ni_patient.group_admin,1,1,1,1
```

- [ ] **Step 7: Add recommendation views**

Create `ni_flag/views/ni_flag_recommendation_views.xml`:

```xml
<?xml version="1.0" encoding="utf-8" ?>
<odoo>
    <record id="ni_flag_recommendation_view_search" model="ir.ui.view">
        <field name="name">ni.flag.recommendation.view.search</field>
        <field name="model">ni.flag.recommendation</field>
        <field name="arch" type="xml">
            <search>
                <field name="patient_id" />
                <field name="encounter_id" />
                <field name="flag_code_id" />
                <field name="source_observation_id" />
                <filter name="pending" string="Pending" domain="[('state', '=', 'pending')]" />
                <filter name="accepted" string="Accepted" domain="[('state', '=', 'accepted')]" />
                <filter name="auto_applied" string="Auto Applied" domain="[('state', '=', 'auto_applied')]" />
                <group expand="0" string="Group By">
                    <filter name="group_flag" string="Flag" context="{'group_by': 'flag_code_id'}" />
                    <filter name="group_state" string="State" context="{'group_by': 'state'}" />
                    <filter name="group_rule" string="Rule" context="{'group_by': 'rule_id'}" />
                </group>
            </search>
        </field>
    </record>
    <record id="ni_flag_recommendation_view_tree" model="ir.ui.view">
        <field name="name">ni.flag.recommendation.view.tree</field>
        <field name="model">ni.flag.recommendation</field>
        <field name="arch" type="xml">
            <tree decoration-muted="state in ['dismissed', 'accepted', 'auto_applied']">
                <field name="patient_id" />
                <field name="encounter_id" optional="show" />
                <field name="flag_code_id" />
                <field name="source_observation_id" />
                <field name="reason" />
                <field name="state" widget="badge" decoration-warning="state == 'pending'" decoration-success="state in ['accepted', 'auto_applied']" />
            </tree>
        </field>
    </record>
    <record id="ni_flag_recommendation_view_form" model="ir.ui.view">
        <field name="name">ni.flag.recommendation.view.form</field>
        <field name="model">ni.flag.recommendation</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <button name="action_accept" type="object" string="Accept" class="btn-primary" attrs="{'invisible': [('state', '!=', 'pending')]}" />
                    <button name="action_dismiss" type="object" string="Dismiss" attrs="{'invisible': [('state', '!=', 'pending')]}" />
                    <field name="state" widget="statusbar" readonly="1" />
                </header>
                <sheet>
                    <group>
                        <group>
                            <field name="patient_id" readonly="1" />
                            <field name="encounter_id" readonly="1" />
                            <field name="flag_code_id" readonly="1" />
                            <field name="flag_id" readonly="1" />
                        </group>
                        <group>
                            <field name="rule_id" readonly="1" />
                            <field name="source_observation_id" readonly="1" />
                            <field name="reason" readonly="1" />
                        </group>
                    </group>
                    <field name="note" />
                </sheet>
            </form>
        </field>
    </record>
    <record id="ni_flag_recommendation_action" model="ir.actions.act_window">
        <field name="name">Flag Recommendations</field>
        <field name="res_model">ni.flag.recommendation</field>
        <field name="view_mode">tree,form</field>
        <field name="context">{'search_default_pending': True}</field>
    </record>
</odoo>
```

- [ ] **Step 8: Add menu and manifest entries**

In `ni_flag/views/ni_flag_menu.xml`, add:

```xml
<menuitem
    id="ni_flag_recommendation_menu"
    name="Flag Recommendations"
    parent="ni_patient.patient_menu_root"
    action="ni_flag_recommendation_action"
    sequence="16"
    groups="ni_patient.group_user"
/>
```

In `ni_flag/__manifest__.py`, add:

```python
"views/ni_flag_recommendation_views.xml",
```

- [ ] **Step 9: Run tests**

Run:

```bash
$ODOO_BIN -c odoo.conf -i ni_flag --test-enable --stop-after-init
```

Expected: recommendation-first and auto-apply tests pass.

- [ ] **Step 10: Commit**

```bash
git add ni_flag/models ni_flag/security/ir.model.access.csv ni_flag/views ni_flag/__manifest__.py ni_flag/tests/test_flag_recommendation.py
git commit -m "[IMP] ni_flag: recommend flags from observations"
```

---

### Task 5: Add Conflict Metadata and Confirmation Wizard

**Files:**

- Modify: `ni_flag/models/ni_flag_code.py`
- Modify: `ni_flag/models/ni_flag_recommendation.py`
- Create: `ni_flag/wizards/__init__.py`
- Create: `ni_flag/wizards/ni_flag_conflict_wizard.py`
- Modify: `ni_flag/__init__.py`
- Modify: `ni_flag/security/ir.model.access.csv`
- Modify: `ni_flag/views/ni_flag_code_views.xml`
- Create: `ni_flag/views/ni_flag_conflict_wizard_views.xml`
- Modify: `ni_flag/__manifest__.py`
- Test: `ni_flag/tests/test_flag_conflict.py`

- [ ] **Step 1: Write failing conflict tests**

Create `ni_flag/tests/test_flag_conflict.py`:

```python
#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestFlagConflict(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "Conflict Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})
        cls.encounter = cls.env["ni.encounter"].create(
            {
                "patient_id": cls.patient.id,
                "class_id": cls.env.ref("ni_patient.class_AMB").id,
            }
        )
        cls.code_fall = cls.env.ref("ni_flag.code_fall")
        cls.code_isolation = cls.env.ref("ni_flag.code_isolation")

    def test_conflicting_code_detects_active_flags(self):
        self.code_fall.conflict_code_ids = [(4, self.code_isolation.id)]
        old_flag = self.env["ni.flag"].create(
            {"patient_id": self.patient.id, "code_id": self.code_isolation.id}
        )
        conflicts = self.code_fall._active_conflicting_flags(self.patient, False)
        self.assertEqual(conflicts, old_flag)

    def test_auto_apply_deactivates_conflicting_flag(self):
        self.code_fall.conflict_code_ids = [(4, self.code_isolation.id)]
        old_flag = self.env["ni.flag"].create(
            {"patient_id": self.patient.id, "code_id": self.code_isolation.id}
        )
        recommendation = self.env["ni.flag.recommendation"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "flag_code_id": self.code_fall.id,
                "rule_id": self.env["ni.flag.recommendation.rule"].create(
                    {
                        "name": "Conflict Auto Rule",
                        "observation_type_id": self.env["ni.observation.type"].create(
                            {"name": "Conflict Obs", "code": "CONFLICT-OBS"}
                        ).id,
                        "flag_code_id": self.code_fall.id,
                        "mode": "auto_apply",
                    }
                ).id,
                "source_observation_id": self.env["ni.observation"].create(
                    {
                        "patient_id": self.patient.id,
                        "encounter_id": self.encounter.id,
                        "type_id": self.env["ni.observation.type"].search([], limit=1).id,
                        "value_float": 1.0,
                    }
                ).id,
            }
        )
        recommendation.action_auto_apply()
        self.assertEqual(old_flag.status, "inactive")
        self.assertTrue(old_flag.period_end)
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
$ODOO_BIN -c odoo.conf -i ni_flag --test-enable --stop-after-init
```

Expected: failure mentions missing conflict fields/helpers.

- [ ] **Step 3: Add conflict fields and helper**

In `ni_flag/models/ni_flag_code.py`, add:

```python
conflict_code_ids = fields.Many2many(
    "ni.flag.code",
    "ni_flag_code_conflict_rel",
    "code_id",
    "conflict_code_id",
    string="Conflicts With",
    help="Active flags with these codes must be removed before this flag is applied.",
)

def _active_conflicting_flags(self, patient, encounter=False):
    self.ensure_one()
    domain = [
        ("patient_id", "=", patient.id),
        ("status", "=", "active"),
        ("code_id", "in", self.conflict_code_ids.ids),
    ]
    if encounter:
        domain = ["|", ("encounter_id", "=", False), ("encounter_id", "=", encounter.id)] + domain
    else:
        domain.append(("encounter_id", "=", False))
    return self.env["ni.flag"].search(domain)
```

- [ ] **Step 4: Deactivate conflicts during auto-apply**

In `ni_flag/models/ni_flag_recommendation.py`, update `action_auto_apply` before creating the new flag:

```python
conflicts = rec.flag_code_id._active_conflicting_flags(rec.patient_id, rec.encounter_id)
conflicts.action_inactive()
flag = Flag.create(rec._flag_values("auto_rule"))
```

- [ ] **Step 5: Add wizard files**

Create `ni_flag/wizards/__init__.py`:

```python
#  Copyright (c) 2026 NSTDA

from . import ni_flag_conflict_wizard
```

Create `ni_flag/wizards/ni_flag_conflict_wizard.py`:

```python
#  Copyright (c) 2026 NSTDA

from odoo import fields, models


class FlagConflictWizard(models.TransientModel):
    _name = "ni.flag.conflict.wizard"
    _description = "Flag Conflict Confirmation"

    recommendation_id = fields.Many2one("ni.flag.recommendation", required=True)
    conflict_flag_ids = fields.Many2many("ni.flag", readonly=True)

    def action_confirm(self):
        self.ensure_one()
        self.conflict_flag_ids.action_inactive()
        self.recommendation_id.action_accept()
```

In `ni_flag/__init__.py`, add:

```python
from . import wizards
```

- [ ] **Step 6: Make recommendation accept open wizard when needed**

In `ni_flag/models/ni_flag_recommendation.py`, update `action_accept`:

```python
def action_accept(self):
    self.ensure_one()
    conflicts = self.flag_code_id._active_conflicting_flags(
        self.patient_id, self.encounter_id
    )
    if conflicts and not self.env.context.get("confirmed_flag_conflict"):
        wizard = self.env["ni.flag.conflict.wizard"].create(
            {
                "recommendation_id": self.id,
                "conflict_flag_ids": [(6, 0, conflicts.ids)],
            }
        )
        return {
            "name": "Confirm Flag Replacement",
            "type": "ir.actions.act_window",
            "res_model": "ni.flag.conflict.wizard",
            "res_id": wizard.id,
            "view_mode": "form",
            "target": "new",
        }
    conflicts.action_inactive()
    flag = self.env["ni.flag"].create(self._flag_values("recommendation"))
    self.write({"state": "accepted", "flag_id": flag.id})
```

In the wizard, call:

```python
self.recommendation_id.with_context(confirmed_flag_conflict=True).action_accept()
```

- [ ] **Step 7: Add access and views**

Append to `ni_flag/security/ir.model.access.csv`:

```csv
access_ni_flag_conflict_wizard_user,access_ni_flag_conflict_wizard_user,model_ni_flag_conflict_wizard,ni_patient.group_user,1,1,1,1
```

In `ni_flag/views/ni_flag_code_views.xml`, add `conflict_code_ids` on the flag code form:

```xml
<field name="conflict_code_ids" widget="many2many_tags" options="{'color_field': 'color'}" />
```

Create `ni_flag/views/ni_flag_conflict_wizard_views.xml`:

```xml
<?xml version="1.0" encoding="utf-8" ?>
<odoo>
    <record id="ni_flag_conflict_wizard_view_form" model="ir.ui.view">
        <field name="name">ni.flag.conflict.wizard.view.form</field>
        <field name="model">ni.flag.conflict.wizard</field>
        <field name="arch" type="xml">
            <form>
                <group>
                    <field name="recommendation_id" readonly="1" />
                    <field name="conflict_flag_ids" readonly="1">
                        <tree>
                            <field name="code_id" />
                            <field name="patient_id" />
                            <field name="encounter_id" />
                            <field name="period_start" />
                        </tree>
                    </field>
                </group>
                <footer>
                    <button name="action_confirm" type="object" string="Replace Flags" class="btn-primary" />
                    <button special="cancel" string="Cancel" />
                </footer>
            </form>
        </field>
    </record>
</odoo>
```

Add the wizard view to `ni_flag/__manifest__.py`:

```python
"views/ni_flag_conflict_wizard_views.xml",
```

- [ ] **Step 8: Run tests**

Run:

```bash
$ODOO_BIN -c odoo.conf -i ni_flag --test-enable --stop-after-init
```

Expected: conflict tests pass.

- [ ] **Step 9: Commit**

```bash
git add ni_flag/models ni_flag/wizards ni_flag/security/ir.model.access.csv ni_flag/views ni_flag/__init__.py ni_flag/__manifest__.py ni_flag/tests/test_flag_conflict.py
git commit -m "[IMP] ni_flag: handle conflicting flags"
```

---

### Task 6: Improve Encounter Form, Kanban, Tree, and Search UX

**Files:**

- Modify: `ni_flag/models/ni_encounter.py`
- Modify: `ni_flag/views/ni_encounter_views.xml`
- Test: `ni_flag/tests/test_flag_views.py`

- [ ] **Step 1: Write view smoke tests**

Create `ni_flag/tests/test_flag_views.py`:

```python
#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestFlagViews(common.TransactionCase):
    def test_encounter_flag_view_inherits_are_valid(self):
        views = [
            "ni_flag.ni_encounter_view_form_inherit",
            "ni_flag.ni_encounter_view_tree_inherit",
            "ni_flag.ni_encounter_view_kanban_inherit",
            "ni_flag.ni_encounter_view_search_inherit",
        ]
        for xmlid in views:
            view = self.env.ref(xmlid)
            self.assertTrue(view.arch_db)
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
$ODOO_BIN -c odoo.conf -i ni_flag --test-enable --stop-after-init
```

Expected: missing view XML IDs for tree, kanban, or search.

- [ ] **Step 3: Add encounter helper fields**

In `ni_flag/models/ni_encounter.py`, add:

```python
active_flag_code_ids = fields.Many2many(
    "ni.flag.code",
    compute="_compute_active_flag_code_ids",
    string="Active Flags",
)
pending_flag_recommendation_count = fields.Integer(
    compute="_compute_pending_flag_recommendation_count"
)

@api.depends("patient_flag_code_ids", "encounter_flag_code_ids")
def _compute_active_flag_code_ids(self):
    for rec in self:
        rec.active_flag_code_ids = rec.patient_flag_code_ids | rec.encounter_flag_code_ids

def _compute_pending_flag_recommendation_count(self):
    data = self.env["ni.flag.recommendation"].read_group(
        [("encounter_id", "in", self.ids), ("state", "=", "pending")],
        ["encounter_id"],
        ["encounter_id"],
    )
    mapped = {d["encounter_id"][0]: d["encounter_id_count"] for d in data}
    for rec in self:
        rec.pending_flag_recommendation_count = mapped.get(rec.id, 0)

def action_flag_recommendations(self):
    self.ensure_one()
    return {
        "name": "Flag Recommendations",
        "type": "ir.actions.act_window",
        "res_model": "ni.flag.recommendation",
        "view_mode": "tree,form",
        "domain": [("encounter_id", "=", self.id)],
        "context": {"search_default_pending": True},
    }
```

- [ ] **Step 4: Replace encounter form flag area**

In `ni_flag/views/ni_encounter_views.xml`, replace the current form inherit body with a compact band after
`//div[hasclass('oe_title')]`:

```xml
<xpath expr="//div[hasclass('oe_title')]" position="after">
    <div name="flag_banner" class="mt-2 mb-3" attrs="{'invisible': [('id', '=', False)]}">
        <div class="o_row">
            <span class="text-muted">Patient Flags</span>
            <field
                name="patient_flag_code_ids"
                widget="many2many_tags"
                options="{'color_field': 'color', 'no_create': False, 'no_open': True}"
                nolabel="1"
            />
        </div>
        <div class="o_row mt-1">
            <span class="text-muted">Encounter Flags</span>
            <field
                name="encounter_flag_code_ids"
                widget="many2many_tags"
                options="{'color_field': 'color', 'no_create': False, 'no_open': True}"
                nolabel="1"
            />
        </div>
    </div>
</xpath>
<xpath expr="//div[@name='button_box']" position="inside">
    <button
        name="action_flag_recommendations"
        type="object"
        class="oe_stat_button"
        icon="fa-lightbulb-o"
        attrs="{'invisible': [('pending_flag_recommendation_count', '=', 0)]}"
    >
        <field name="pending_flag_recommendation_count" widget="statinfo" string="Flag Suggestions" />
    </button>
</xpath>
```

- [ ] **Step 5: Add encounter tree flags**

Add a tree inherit in `ni_flag/views/ni_encounter_views.xml`:

```xml
<record id="ni_encounter_view_tree_inherit" model="ir.ui.view">
    <field name="name">ni.encounter.view.tree.flag</field>
    <field name="model">ni.encounter</field>
    <field name="inherit_id" ref="ni_patient.ni_encounter_view_tree" />
    <field name="arch" type="xml">
        <xpath expr="//field[@name='patient_id']" position="after">
            <field
                name="active_flag_code_ids"
                widget="many2many_tags"
                options="{'color_field': 'color', 'no_open': True}"
                optional="show"
            />
        </xpath>
    </field>
</record>
```

- [ ] **Step 6: Add encounter kanban flags**

Add a kanban inherit in `ni_flag/views/ni_encounter_views.xml`:

```xml
<record id="ni_encounter_view_kanban_inherit" model="ir.ui.view">
    <field name="name">ni.encounter.view.kanban.flag</field>
    <field name="model">ni.encounter</field>
    <field name="inherit_id" ref="ni_patient.ni_encounter_view_kanban" />
    <field name="arch" type="xml">
        <xpath expr="//kanban/templates" position="before">
            <field name="active_flag_code_ids" />
        </xpath>
        <xpath expr="//field[@name='reason_ids']/ancestor::div[1]" position="after">
            <div class="my-1">
                <field
                    name="active_flag_code_ids"
                    widget="many2many_tags"
                    options="{'color_field': 'color', 'no_open': True}"
                />
            </div>
        </xpath>
    </field>
</record>
```

- [ ] **Step 7: Add encounter search filters**

Add a search inherit in `ni_flag/views/ni_encounter_views.xml`:

```xml
<record id="ni_encounter_view_search_inherit" model="ir.ui.view">
    <field name="name">ni.encounter.view.search.flag</field>
    <field name="model">ni.encounter</field>
    <field name="inherit_id" ref="ni_patient.ni_encounter_view_search" />
    <field name="arch" type="xml">
        <xpath expr="//search/field[@name='patient_id']" position="after">
            <field name="active_flag_code_ids" string="Flag" />
        </xpath>
        <xpath expr="//filter[@name='encounter']" position="after">
            <filter name="has_active_flag" string="Has Active Flag" domain="[('active_flag_code_ids', '!=', False)]" />
            <filter name="has_pending_flag_recommendation" string="Has Flag Suggestion" domain="[('pending_flag_recommendation_count', '&gt;', 0)]" />
        </xpath>
    </field>
</record>
```

- [ ] **Step 8: Run tests**

Run:

```bash
$ODOO_BIN -c odoo.conf -i ni_flag --test-enable --stop-after-init
```

Expected: view smoke tests pass.

- [ ] **Step 9: Manual UX check**

Open `http://localhost:16669` and check:

- Encounter form shows Patient Flags and Encounter Flags near the title.
- Encounter kanban cards show active flags without opening the card.
- Encounter tree shows active flags after patient.
- Encounter search can filter by active flags and pending flag suggestions.

- [ ] **Step 10: Commit**

```bash
git add ni_flag/models/ni_encounter.py ni_flag/views/ni_encounter_views.xml ni_flag/tests/test_flag_views.py
git commit -m "[IMP] ni_flag: improve encounter flag UX"
```

---

### Task 7: Improve Flag Reports

**Files:**

- Modify: `ni_flag/views/ni_flag_views.xml`
- Modify: `ni_flag/views/ni_flag_recommendation_views.xml`
- Modify: `ni_flag/views/ni_flag_menu.xml`
- Test: `ni_flag/tests/test_flag_views.py`

- [ ] **Step 1: Extend view smoke tests for report actions**

Add to `ni_flag/tests/test_flag_views.py`:

```python
def test_flag_report_actions_exist(self):
    actions = [
        "ni_flag.ni_flag_action",
        "ni_flag.ni_flag_recommendation_action",
    ]
    for xmlid in actions:
        action = self.env.ref(xmlid)
        self.assertTrue(action.name)
```

- [ ] **Step 2: Add source fields to flag search/report**

In `ni_flag/views/ni_flag_views.xml`, add search fields:

```xml
<field name="origin" />
<field name="source_observation_id" />
<field name="recommendation_id" />
```

Add group-by filters:

```xml
<filter name="group_origin" string="Origin" context="{'group_by': 'origin'}" />
<filter name="group_author" string="Author" context="{'group_by': 'author_id'}" />
```

- [ ] **Step 3: Add report columns to flag tree**

In `ni_flag/views/ni_flag_views.xml`, add after `code_id`:

```xml
<field name="origin" widget="badge" optional="show" />
<field name="source_observation_id" optional="show" />
<field name="evidence_summary" optional="hide" />
```

- [ ] **Step 4: Improve pivot and graph**

In `ni_flag/views/ni_flag_views.xml`, update pivot:

```xml
<pivot>
    <field name="code_id" type="row" />
    <field name="origin" type="col" />
    <field name="status" type="col" />
</pivot>
```

Update graph:

```xml
<graph type="bar" stacked="True">
    <field name="code_id" type="row" />
    <field name="origin" type="col" />
</graph>
```

- [ ] **Step 5: Add pending recommendation report defaults**

In `ni_flag/views/ni_flag_recommendation_views.xml`, keep the action context:

```xml
<field name="context">{'search_default_pending': True}</field>
```

Ensure tree columns include:

```xml
<field name="source_observation_id" />
<field name="reason" />
<field name="rule_id" optional="show" />
```

- [ ] **Step 6: Run tests**

Run:

```bash
$ODOO_BIN -c odoo.conf -i ni_flag --test-enable --stop-after-init
```

Expected: view/action tests pass.

- [ ] **Step 7: Manual report check**

Open the Flag menu and verify:

- Active flags report shows origin and source observation.
- Pivot can group active flags by code and origin.
- Recommendations report defaults to pending.
- Accepted/auto-applied recommendations link to the created flag.

- [ ] **Step 8: Commit**

```bash
git add ni_flag/views/ni_flag_views.xml ni_flag/views/ni_flag_recommendation_views.xml ni_flag/views/ni_flag_menu.xml ni_flag/tests/test_flag_views.py
git commit -m "[IMP] ni_flag: improve flag reports"
```

---

### Task 8: Tighten Duplicate Recommendation and Duplicate Flag Behavior

**Files:**

- Modify: `ni_flag/models/ni_observation.py`
- Modify: `ni_flag/models/ni_flag_recommendation.py`
- Modify: `ni_flag/tests/test_flag_recommendation.py`

- [ ] **Step 1: Add duplicate prevention tests**

Add to `ni_flag/tests/test_flag_recommendation.py`:

```python
def test_same_observation_rule_does_not_create_duplicate_recommendations(self):
    rule = self.env["ni.flag.recommendation.rule"].create(
        {
            "name": "No duplicate recommendation",
            "observation_type_id": self.obs_type.id,
            "interpretation_id": self.interpretation.id,
            "flag_code_id": self.flag_code.id,
            "scope": "encounter",
            "mode": "recommend",
        }
    )
    observation = self.env["ni.observation"].create(
        {
            "patient_id": self.patient.id,
            "encounter_id": self.encounter.id,
            "type_id": self.obs_type.id,
            "value_float": 12.0,
            "interpretation_id": self.interpretation.id,
        }
    )
    observation.write({"value_float": 13.0})
    recommendations = self.env["ni.flag.recommendation"].search(
        [("source_observation_id", "=", observation.id), ("rule_id", "=", rule.id)]
    )
    self.assertEqual(len(recommendations), 1)

def test_accept_recommendation_reuses_existing_active_flag(self):
    self.env["ni.flag"].create(
        {
            "patient_id": self.patient.id,
            "encounter_id": self.encounter.id,
            "code_id": self.flag_code.id,
        }
    )
    recommendation = self.env["ni.flag.recommendation"].create(
        {
            "patient_id": self.patient.id,
            "encounter_id": self.encounter.id,
            "flag_code_id": self.flag_code.id,
            "rule_id": self.env["ni.flag.recommendation.rule"].create(
                {
                    "name": "Reuse active flag",
                    "observation_type_id": self.obs_type.id,
                    "flag_code_id": self.flag_code.id,
                }
            ).id,
            "source_observation_id": self.env["ni.observation"].create(
                {
                    "patient_id": self.patient.id,
                    "encounter_id": self.encounter.id,
                    "type_id": self.obs_type.id,
                    "value_float": 12.0,
                }
            ).id,
        }
    )
    recommendation.action_accept()
    flags = self.env["ni.flag"].search(
        [
            ("patient_id", "=", self.patient.id),
            ("encounter_id", "=", self.encounter.id),
            ("code_id", "=", self.flag_code.id),
            ("status", "=", "active"),
        ]
    )
    self.assertEqual(len(flags), 1)
```

- [ ] **Step 2: Implement active flag reuse**

In `ni_flag/models/ni_flag_recommendation.py`, add:

```python
def _active_matching_flag(self):
    self.ensure_one()
    domain = [
        ("patient_id", "=", self.patient_id.id),
        ("code_id", "=", self.flag_code_id.id),
        ("status", "=", "active"),
    ]
    if self.encounter_id:
        domain.append(("encounter_id", "=", self.encounter_id.id))
    else:
        domain.append(("encounter_id", "=", False))
    return self.env["ni.flag"].search(domain, limit=1)
```

Use it in `action_accept` and `action_auto_apply`:

```python
flag = rec._active_matching_flag()
if not flag:
    flag = Flag.create(rec._flag_values("recommendation"))
else:
    flag.write(
        {
            "source_observation_id": rec.source_observation_id.id,
            "recommendation_id": rec.id,
        }
    )
rec.write({"state": "accepted", "flag_id": flag.id})
```

For auto-apply, use origin `"auto_rule"` when creating a new flag.

- [ ] **Step 3: Run tests**

Run:

```bash
$ODOO_BIN -c odoo.conf -i ni_flag --test-enable --stop-after-init
```

Expected: duplicate recommendation and active flag reuse tests pass.

- [ ] **Step 4: Commit**

```bash
git add ni_flag/models/ni_flag_recommendation.py ni_flag/models/ni_observation.py ni_flag/tests/test_flag_recommendation.py
git commit -m "[IMP] ni_flag: prevent duplicate flag recommendations"
```

---

### Task 9: Final Verification and PR Notes

**Files:**

- Modify: `ni_flag/README.md`
- Read: all modified `ni_flag/*`

- [ ] **Step 1: Update README**

In `ni_flag/README.md`, add sections:

```markdown
## Observation-driven flag recommendations

Flag recommendation rules map observation types and optional interpretation or value-code matches to flag codes. Rules recommend
by default. Admins may mark selected rules as auto-apply.

Recommended and auto-created flags keep the source observation on the flag detail form so staff can see why the flag exists.

## Conflicting flags

Flag codes can define conflicting flag codes. When a user accepts a recommendation that conflicts with active flags, a
confirmation wizard shows the flags that will be deactivated. Auto-apply rules deactivate conflicting flags automatically and
close the old flags with `period_end`.
```

- [ ] **Step 2: Run Python syntax check**

Run:

```bash
python -m py_compile ni_flag/models/*.py ni_flag/wizards/*.py ni_flag/tests/*.py
```

Expected: no syntax errors.

- [ ] **Step 3: Run module tests**

Run:

```bash
$ODOO_BIN -c odoo.conf -i ni_flag --test-enable --stop-after-init
```

Expected: all `ni_flag` tests pass.

- [ ] **Step 4: Run pre-commit**

Run:

```bash
pre-commit run --all-files
```

Expected: formatting/lint checks pass. If translations are needed for new UI strings, regenerate `ni_flag/i18n/th.po` using the
repository translation guidance.

- [ ] **Step 5: Manual UX verification**

Check in Odoo at `http://localhost:16669`:

- Patient form shows patient-level active flags.
- Encounter form shows patient flags and encounter flags near the title.
- Encounter kanban and tree show active flags.
- Pending recommendation appears after a matching observation is created.
- Accepting a recommendation creates an active flag.
- Flag detail shows source observation and recommendation.
- Conflict wizard appears for conflicting user acceptance.
- Auto-apply rule creates a flag and deactivates conflicting old flags.
- Flag reports show origin, evidence, and pending recommendations.

- [ ] **Step 6: Update PR description**

Add to PR #95:

```markdown
Additional improvements:

- Encounter form, kanban, tree, and search views now expose active flags for faster triage.
- Observation-driven rules create flag recommendations by default.
- Admin-selected rules may auto-apply flags.
- Recommended and auto-created flags keep source observation evidence on the flag detail.
- Conflicting flags are handled with user confirmation or admin auto-replacement.
- Flag reports include origin and evidence context.
```

- [ ] **Step 7: Final commit**

```bash
git add ni_flag/README.md
git commit -m "[IMP] ni_flag: document recommendations and conflicts"
```

---

## Self-Review

Spec coverage:

- Encounter form/kanban/tree UX: covered by Task 6.
- Better flag-related reports: covered by Task 7.
- Recommendation-first observation-driven flags: covered by Tasks 3 and 4.
- Admin-only auto-apply rules: covered by Tasks 3 and 4.
- Show observation that caused the flag: covered by Task 2 and Task 7.
- Conflict handling with user confirmation or admin auto-removal: covered by Task 5.
- Duplicate prevention: covered by Task 8.
- Verification and PR notes: covered by Task 9.

Placeholder scan:

- No unresolved placeholder markers are present.
- Commands and expected outcomes are explicit.
- File paths are explicit.

Type consistency:

- `source_observation_id`, `recommendation_id`, `origin`, `ni.flag.recommendation`, and `ni.flag.recommendation.rule` are used
  consistently across tasks.
- Recommendation states are `pending`, `accepted`, `dismissed`, and `auto_applied`.
- Rule modes are `recommend` and `auto_apply`.

## Execution Options

Plan complete and saved to `docs/superpowers/plans/2026-06-07-ni-flag-pr95-improvement.md`.

Two execution options:

1. Subagent-Driven (recommended): dispatch a fresh subagent per task, review between tasks, fast iteration.
2. Inline Execution: execute tasks in this session using checkpoints after each task.
