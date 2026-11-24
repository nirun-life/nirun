# Practitioner Role (`ni_practitioner_role`)

Odoo 18.0 module that extends user roles with practitioner onboarding, verification,
employee creation, and QR-based role registration flows.

## Purpose

`ni_practitioner_role` adapts `base_user_role` for healthcare staff onboarding. It lets
each role publish a registration link, tracks whether practitioner accounts are verified
before login, and can create matching employee records with role-driven categories.

## Main Models

| Model            | Role                                                           |
| ---------------- | -------------------------------------------------------------- |
| `res.users`      | Extended with verification state and employee creation helpers |
| `res.users.role` | Extended with onboarding token, QR code, and user counters     |

## Workflow and Behavior

- `models/res_users.py` adds a `verified` flag and blocks login in
  `_check_credentials()` until the account has been verified.
- `action_verify()` and `action_verify_employee()` can create an `hr.employee` record
  for the user and populate the employee license number from the login.
- `models/res_users_role.py` adds `employee_category_ids`, company-dependent invitation
  tokens (created with the role, or with the "Create Invitation Link" button for another
  company), registration URLs, QR-code generation, and per-role counts for users and
  unverified users.
- Role verification can also copy employee categories from the assigned roles onto the
  generated employee record.

## Views, Website Flow, and Security

- `controller/main.py` serves QR-code downloads and the public practitioner registration
  flow at `/practitioner/register/<company_id>/<token>`. The token decides the company
  and the role: posted values never do. A signed in user only registers their own
  account, and only for a company they belong to.
- `views/ni_practitioner_role_template.xml` contains the registration and success
  templates.
- `views/res_user_role_views.xml` and `views/res_user_views.xml` expose onboarding and
  verification actions in the backend.
- `security/ir_rule.xml` applies company-aware access restrictions for role-linked
  users.

## Dependencies

- `base_user_role`
- `auth_signup`
- `ni_practitioner` (licence number of the employee)
- Python `qrcode`
- Optional: `base_user_role_company` (AGPL-3, so not a dependency). When it is
  installed, the registration form also sets the company of the role line.

## Upgrade Notes

- `migrations/18.0.1.0.0` copies the invitation tokens from `ir_property` into the jsonb
  column of 18.0, because OpenUpgrade converts company-dependent fields of the core
  modules only.
- Roles without a token for a company no longer get one when the link is read, only
  through the button.

## Verification

- `tests/` covers the invitation token per company, verification and the registration
  form.
- Re-check the practitioner registration flow from invitation link through account
  creation and post-registration confirmation.
- Confirm unverified users cannot authenticate until verification is completed.
- Review employee creation and role-to-category propagation after changes to user or
  role logic.
