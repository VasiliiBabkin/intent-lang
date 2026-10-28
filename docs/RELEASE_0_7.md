# Sedrava — pre-release process

Sedrava is an experimental language. Its new Python distribution `sedrava` is **not yet published**. The repository currently remains `VasiliiBabkin/intent-lang` until a separately approved rename.

## Validate a release candidate

1. Run the complete Python test suite and the Android Compose workflow.
2. Build the wheel and sdist: `python -m build`.
3. Validate metadata: `python -m twine check dist/*` and `python scripts/audit_dist.py`.
4. Install the built wheel in a clean virtual environment and test `sedrava --version`, `sedrava check`, `sedrava test` and both generators against `examples/workflow.sdr`.
5. Review the final GitHub repository name, PyPI project-name availability and Trusted Publisher configuration.
6. Only after separate approval, choose a new pre-1.0 version and publish using an explicitly reviewed release workflow.

The old project release records remain available in Git history. The previously published `intent-lng` distribution is separate and is not modified by this process.
