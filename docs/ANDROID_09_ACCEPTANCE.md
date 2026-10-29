# Sedrava 0.9 — Android device acceptance

Status: PASS for the reference application on a physical Android 16 phone (2026-10-29). This is an observed manual test, not a certification or exhaustive conformance suite.

## Verified

- Workflow demo launches and its basic actions work.
- Sedrava 0.9 Lab launches; actions update progress and sessions; derived `reached` and conditional messages respond correctly.
- Accepted goal edits are reflected in state.
- Relaunch preserves goal, progress and sessions, including observed `goal=5`, `progress=3`, `sessions=3`.
- Invalid goal `55` is rejected with a visible error and preserved editable draft; accepted goal remains `5`.
- Goal `3` with progress `5` is rejected; accepted goal remains `20` and counters remain unchanged.
- Input `2147483648` is rejected with visible error, preserving accepted goal `5` and the editable draft.

## Remaining release limitations

- Manual tests do not establish Web/Android semantic parity for all cases, accessibility compliance or complete security review.
- Physical-device tests of corrected input after overflow and persistence of rejected draft across restart are not independently evidenced.
- GitHub alpha release and PyPI publication are separate actions. PyPI publication remains postponed.

Source: user-supplied Android screenshots and explicit confirmation of relaunch persistence in the project conversation. See [reference application test plan](REFERENCE_09.md).
