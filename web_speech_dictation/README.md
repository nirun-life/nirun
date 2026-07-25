# Web Speech Dictation

Adds a browser-native speech-to-text dictation modal to editable backend HTML and multiline text fields.

## Behavior

- Each field shows only a microphone-only trigger button: inline after the textarea for `TextField` (same `d-inline-flex`
  wrapper + trailing icon pattern as `web.FormEmailField`/`web.FormPhoneField`), overlaid bottom-right of the editable content
  area for `HtmlField` (clear of the toolbar, which is anchored top).
- Clicking the trigger snapshots the field's current caret/selection, then opens a `DictationModal` dialog that auto-starts
  listening.
- Recognized speech is staged in a transcript buffer inside the modal — nothing is written to the field while dictating. The
  buffer accumulates across as many pause/resume cycles as the user runs in one modal session (each resume spins up a fresh
  `SpeechRecognition` instance internally; the buffer treats it as one continuous session). Unfinalized (interim) speech is
  shown live but dropped on pause, not buffered.
- Confirming applies the buffered transcript using one of three insert modes: at the snapshotted cursor (default), at the end of
  the field, or replacing the field's entire content. For `HtmlField`, "at cursor" and "at end" use Odoo Editor's own insert
  command to preserve undo/dirty-state handling; "replace" clears the editable and inserts the transcript as plain text
  (dictation output is never HTML). The code-view textarea only supports "at cursor".
- Any way of leaving the modal other than Confirm (header close, backdrop, Escape) discards the buffer — there is no secondary
  confirmation step.
- Uses the browser `SpeechRecognition` API only; no server endpoint or credential is introduced. Lists the instance's active
  Odoo languages, defaults to the current user's language, and remembers the last-picked language in browser local storage
  (shared across every field's own controller instance). The language picker is disabled while actively listening — pause first
  to switch languages. The chosen insert mode always resets to "at cursor" on next open; it is not persisted.
- Displays a disabled trigger when the browser does not provide speech recognition — the modal is simply unreachable in that
  case.

## Extension points and verification

- `static/src/dictation/dictation_controller.js` is the shared seam: recognition lifecycle, transcript buffering,
  cursor/selection snapshot-and-restore, and per-mode field writing. It has no OWL dependency and is unit-testable on its own.
- `static/src/dictation/dictation_modal.js`/`.xml` is the `DictationModal` dialog — pure UI wiring around the controller, no
  independent logic.
- The `TextField` and `HtmlField` widget patches only render the mic trigger and open the modal; `HtmlField` additionally
  supplies the wysiwyg/code-view-specific write logic to the controller via its `applyTranscript` callback.
- `static/tests/dictation_controller_tests.js` is a QUnit unit suite covering buffer accumulation across pause/resume, the three
  insert modes, and discard — run via Odoo's browser-based QUnit test runner (`/web/tests`). It is not exercised by this repo's
  `oca_run_tests`/`--test-enable` toolchain (that runs Python `TransactionCase` tests only), so check it manually after touching
  the controller.
- End-to-end dictation (actual recognized speech landing in a field) still requires manual verification in Chrome or Edge, since
  CI cannot exercise a real microphone.
