# PyPI Publishing

The package metadata is ready for PyPI project `inbox-report` at the current version in `pyproject.toml`.

Publishing is local-only. This repository intentionally does not include an automated release workflow.

Do not paste a PyPI password or token into chat, issues, commits, or repository settings.

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

## Local Upload

Create a PyPI project API token from your PyPI account, then export it only in your local shell:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-...
make publish
```

`make publish` rebuilds the package, runs `twine check`, and uploads the files in `dist/`.

After the upload, verify the published version:

```bash
python3 -m pip index versions inbox-report
python3 -m pip install --upgrade "inbox-report[pdf]"
inbox-report --version
```

Do not commit tokens. Do not paste tokens into issues, PRs, chat, or screenshots.

## Name

The package name is:

```text
inbox-report
```

The console command remains:

```text
inbox-report
```
