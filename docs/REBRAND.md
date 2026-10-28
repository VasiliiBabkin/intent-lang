# Sedrava — Rebrand and release checklist

## Identity

- International name: **Sedrava Programming Language**; Russian: **Седрава**.
- Python distribution and CLI: `sedrava`.
- Runtime modules: `sedrava.py`, `sedrava_core.py`, `sedrava_cli.py`.
- Source extension: `.sdr`; no legacy aliases.
- Generated Android namespace/application ID: `org.sedrava.generated`.
- Repository is **still** `VasiliiBabkin/intent-lang`; its rename requires separate approval.
- `sedrava.com` is a possible future domain, **not** a registered or official site.

## Release status

The Sedrava package has **not** been published on PyPI. The existing source version `0.7.0a1` is retained to avoid conflating a rebrand with a feature release. Proposed next release is **0.7.1a1** after testing and explicit approval. Do not reuse a published version number for a different artifact.

## Owner actions after merging

1. Approve and perform the GitHub repository rename from `intent-lang` to `sedrava` in GitHub Settings → General → Repository name. Update repository descriptions, social links and local Git remotes.
2. Check that `sedrava` is available as a PyPI project name; availability is **not guaranteed**. Configure PyPI Trusted Publishing for the final repository and release workflow; never reuse the former package's publisher configuration blindly.
3. Verify GitHub Actions, badges, documentation links and artifact names against the new repository URL.
4. Set the next approved pre-1.0 version, rebuild wheel and sdist, run the clean-install smoke tests and package audit, and publish **only after explicit approval**.
5. Decide separately whether to acquire `sedrava.com`; do not link to it as official before registration and deployment.

Historical Git commits, existing releases and artifacts are preserved. The old PyPI project `intent-lng` is a separate distribution and is not deleted or modified by this rebrand.
