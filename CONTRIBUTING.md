# Contributing

Use a separate branch and fictional data. Run:

```sh
uv sync --frozen
uv run --frozen python -m unittest discover -s tests -v
uv run --frozen python scripts/smoke_mcp.py
uv run --frozen python scripts/check_public_files.py
```

Add meaningful regression tests for changed operation scope, auth behavior or approval rules. Keep Google calls mocked in the unit suite. Never use a live account in an automated test by default. Document schema/version changes and preserve host-level approval requirements.

When changing dependencies, regenerate uv.lock deliberately and rerun installation in a clean directory. Do not commit .env, real MCP settings, credential files, audit output, client fixtures or local machine paths. The lightweight public-file check complements manual review and a secret scanner; it is not a guarantee that arbitrary secrets will be detected.

Submit a pull request explaining the concrete behavior, tests and limits. Contributions are made under the repository's MIT license. Security reports follow SECURITY.md.

