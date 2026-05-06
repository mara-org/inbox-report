# PyPI Publishing

Package name:

```text
inbox-report
```

Build locally:

```bash
python3 -m pip install -r requirements-dev.txt
make package PYTHON=python3
```

Upload locally with a PyPI token:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-...
make publish PYTHON=python3
```

Do not commit tokens or paste them into chat, issues, PRs, or screenshots.

After publishing:

```bash
python3 -m pip install --upgrade "inbox-report[pdf]"
inbox-report --version
```
