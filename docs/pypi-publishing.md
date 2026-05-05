# PyPI Publishing

The package metadata is ready for PyPI project `inbox-report` at the current version in `pyproject.toml`.

Preferred publishing uses PyPI Trusted Publishers with GitHub Actions. Do not paste a PyPI password or token into chat, issues, commits, or workflow files.

## Local Build

```bash
python3 -m pip install -r requirements-dev.txt
make package
```

That creates:

- `dist/*.tar.gz`
- `dist/*.whl`

and runs:

```bash
python3 -m twine check dist/*
```

## Test Install Locally

```bash
python3 -m pip install -e ".[pdf]"
inbox-report --version
make demo
```

## Trusted Publisher Setup

In PyPI's **Publishing** page, add a pending GitHub trusted publisher:

```text
PyPI Project Name: inbox-report
Owner: mara-org
Repository name: inbox-report
Workflow name: publish.yml
Environment name: pypi
```

Use `inbox-report` as the repository name, not the full GitHub URL.

The workflow file must exist at:

```text
.github/workflows/publish.yml
```

After adding the pending publisher in PyPI, publish by pushing a version tag such as `v1.0.1`, creating a GitHub Release, or manually running the `publish` workflow from GitHub Actions.

## Token Fallback

Trusted publishing is preferred. If you still need to publish from a local shell, use a PyPI API token stored locally as an environment variable:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-...
make publish
```

Do not commit tokens. Do not paste tokens into issues, PRs, or chat.

## Name

The package name is:

```text
inbox-report
```

The console command remains:

```text
inbox-report
```
