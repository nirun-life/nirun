# definition_id locks on ANY device request, not just approved ones

`ni.device.write()` now blocks changing `definition_id` once the device has at least one `ni.device.request` record, in any
state — draft, pending, approved, or rejected. A narrower rule (lock only once a request is _approved_) was considered, since
draft/rejected requests never actually changed the device's holder or status.

The broader rule was chosen because a request record — even a rejected one — means the device has already entered the
operational request/approval workflow and is no longer purely "being set up." Locking on first request avoids a device drifting
between definitions mid-workflow (e.g. a pending hold request approved against stale manufacturer/model/type data copied from a
definition that was swapped out after the request was filed). The trade-off: a device whose only request was rejected keeps
`definition_id` locked forever, with no unlock path. If that turns out to be too strict in practice, narrowing the guard to
`request_ids.filtered(lambda r: r.state != "rejected")` is the reversal point.
