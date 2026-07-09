# Device price is a one-time default from the definition, not a resynced field

`ni.device.definition` gained a `price` field to reduce manual data entry, following the existing `_compute_from_definition`
pattern that already propagates `manufacturer_id`, `model_number`, `type_ids`, and `image_1920` from the definition to each
device. Unlike `manufacturer_id`/`model_number`, which resync every time `definition_id` changes (silently overwriting any
manual edit), `price` follows the `image_1920` guard instead: it only fills in when the device's own `price` is still unset
(`if dfn.price and not rec.price`), and is never overwritten again once a value exists.

This was a deliberate choice: price is routinely edited per-device after purchase (discounts, used equipment, currency
differences) and should not silently revert to the definition's list price on a later `definition_id` correction. Anyone
extending `_compute_from_definition` should keep this asymmetry — resync fields like `manufacturer_id`/`model_number` describe
the device's identity and should track the template; `price` (like `image_1920`) is device-specific data that only needs a
starting value.
