# Partner - Religions (`partner_religion`)

## Purpose

Adds a religion master-data model and links contacts to it.

## Main Components

- `res.religion` Hierarchical religion model with `name`, `abbr`, `parent_id`, `child_ids`, `sequence`, `color`, and `active`.
- `res.partner` extension Adds `religion_id`.

## Data, Views, and Security

- Seeds a starter religion hierarchy including Dharmic and Abrahamic groups plus child religions.
- Religion management views: standalone action plus tree, form, and search views.
- Partner form: adds `religion_id` after `lang`.
- Security: grants model access for `res.religion`.

## Dependencies

- `base`

## Notes

- Religion search supports both `name` and `abbr`.
- The hierarchy is protected against recursive parent relationships, and religion names must be unique.
