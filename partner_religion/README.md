# Partner - Religions (`partner_religion`)

## Purpose

Adds a religion master-data model and links contacts to it.

## Main Components

- `res.religion` Hierarchical religion model with `name`, `abbr`, `parent_id`,
  `child_ids`, `sequence`, `color`, and `active`.
- `res.partner` extension Adds `religion_id`.

## Data, Views, and Security

- Seeds a starter religion hierarchy including Dharmic and Abrahamic groups plus child
  religions.
- Religion management views: standalone action plus list, form, and search views.
- Partner form: adds `religion_id` after `lang`.
- Security: internal, portal and public users can read `res.religion`; contact managers
  (`base.group_partner_manager`) have full access.

## Verification

- `tests/test_res_religion.py`: display name formats, name search and the recursion
  check.

## Dependencies

- `base`

## Notes

- Religion search supports both `name` and `abbr` (`_rec_names_search`);
  `_search_display_name` makes a multi-word query match every word in `name`.
- `display_name` is computed in `_compute_display_name`. The context keys `show_parent`,
  `show_abbr` and `only_abbr` change the format.
- The hierarchy is protected against recursive parent relationships, and religion names
  must be unique.
