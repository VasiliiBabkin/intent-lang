# Sedrava — Rebrand and release checklist

## Identity

- International name: **Sedrava Programming Language**; Russian: **Седрава**.
- Python distribution and CLI: `sedrava`.
- Runtime modules: `sedrava.py`, `sedrava_core.py`, `sedrava_cli.py`.
- Source extension: `.sdr`; no legacy aliases.
- Generated Android namespace/application ID: `org.sedrava.generated`.
- Repository rename completed: `VasiliiBabkin/sedrava`.
- `sedrava.com` is a possible future domain, **not** a registered or official site.

## Release status

The Sedrava package has **not** been published on PyPI. The first Sedrava GitHub alpha candidate is **0.7.1a1**. The package remains unpublished on PyPI. A GitHub Release must be created separately after CI passes. Do not reuse a published version number for a different artifact.

## Owner actions after merging

1. GitHub repository rename completed. Update local Git remotes to `https://github.com/VasiliiBabkin/sedrava.git` and review repository descriptions and social links.
2. Check that `sedrava` is available as a PyPI project name; availability is **not guaranteed**. Configure PyPI Trusted Publishing for the final repository and release workflow; never reuse the former package's publisher configuration blindly.
3. Verify GitHub Actions, badges, documentation links and artifact names against the new repository URL.
4. Set the next approved pre-1.0 version, rebuild wheel and sdist, run the clean-install smoke tests and package audit, and publish **only after explicit approval**.
5. Decide separately whether to acquire `sedrava.com`; do not link to it as official before registration and deployment.

Historical Git commits, existing releases and artifacts are preserved. The old PyPI project `intent-lng` is a separate distribution and is not deleted or modified by this rebrand.
