PYTHON ?= /usr/bin/python3
OUT_DIR ?= .demo
REPORT_DIR ?= reports
INPUT ?=
SAMPLE_MBOX := $(OUT_DIR)/sample.mbox

.PHONY: help install install-dev check test demo report audit path-smoke agent-check package publish clean

help:
	@/bin/echo 'Inbox Application Reporter'
	@/bin/echo ''
	@/bin/echo 'Commands:'
	@/bin/echo '  make install   install optional PDF deps'
	@/bin/echo '  make install-dev install packaging deps'
	@/bin/echo '  make check     run compile, help, version, and tests'
	@/bin/echo '  make test      run unit tests'
	@/bin/echo '  make demo      build a fake mailbox and generate reports'
	@/bin/echo '  make report INPUT=/path/to/export run on a real local export'
	@/bin/echo '  make audit INPUT=/path/to/export include noisy weak matches'
	@/bin/echo '  make path-smoke verify paths with spaces and Arabic text'
	@/bin/echo '  make agent-check run check, demo, and package'
	@/bin/echo '  make package   build local PyPI artifacts'
	@/bin/echo '  make publish   upload dist to PyPI using local twine env vars'
	@/bin/echo '  make clean     remove local demo outputs and caches'

install:
	$(PYTHON) -m pip install -r requirements.txt

install-dev:
	$(PYTHON) -m pip install -r requirements-dev.txt

check:
	$(PYTHON) -B -m py_compile inbox_application_reporter.py
	$(PYTHON) inbox_application_reporter.py --help >/dev/null
	$(PYTHON) inbox_application_reporter.py --version
	$(PYTHON) -m unittest discover -s tests -v

test:
	$(PYTHON) -m unittest discover -s tests -v

demo:
	/bin/mkdir -p $(OUT_DIR)
	$(PYTHON) tests/make_sample_mbox.py $(SAMPLE_MBOX)
	$(PYTHON) inbox_application_reporter.py $(SAMPLE_MBOX) \
		--out $(OUT_DIR)/applications.csv \
		--summary-out $(OUT_DIR)/applications_summary.csv \
		--student-summary-out $(OUT_DIR)/student_summary.csv \
		--html-out $(OUT_DIR)/applications_report.html \
		--pdf-out $(OUT_DIR)/applications_report.pdf
	@/bin/echo 'demo outputs are in $(OUT_DIR)/'

report:
	@if /bin/test -z "$(INPUT)"; then \
		/bin/echo 'usage: make report INPUT=/path/to/Mail.mbox'; \
		/bin/echo '   or: make report INPUT=/path/to/eml-folder'; \
		exit 2; \
	fi
	/bin/mkdir -p "$(REPORT_DIR)"
	$(PYTHON) inbox_application_reporter.py "$(INPUT)" \
		--out "$(REPORT_DIR)/applications.csv" \
		--summary-out "$(REPORT_DIR)/applications_summary.csv" \
		--student-summary-out "$(REPORT_DIR)/student_summary.csv" \
		--html-out "$(REPORT_DIR)/applications_report.html" \
		--pdf-out "$(REPORT_DIR)/applications_report.pdf"
	@/bin/echo 'report outputs are in $(REPORT_DIR)/'

audit:
	@if /bin/test -z "$(INPUT)"; then \
		/bin/echo 'usage: make audit INPUT=/path/to/Mail.mbox'; \
		/bin/echo '   or: make audit INPUT=/path/to/eml-folder'; \
		exit 2; \
	fi
	/bin/mkdir -p "$(REPORT_DIR)"
	$(PYTHON) inbox_application_reporter.py "$(INPUT)" --include-weak \
		--out "$(REPORT_DIR)/applications.csv" \
		--summary-out "$(REPORT_DIR)/applications_summary.csv" \
		--student-summary-out "$(REPORT_DIR)/student_summary.csv" \
		--html-out "$(REPORT_DIR)/applications_report.html" \
		--pdf-out "$(REPORT_DIR)/applications_report.pdf"
	@/bin/echo 'audit outputs are in $(REPORT_DIR)/'

path-smoke:
	/bin/mkdir -p "$(OUT_DIR)/مسار تجريبي"
	$(PYTHON) tests/make_sample_mbox.py "$(OUT_DIR)/مسار تجريبي/sample mail.mbox"
	$(MAKE) report INPUT="$(OUT_DIR)/مسار تجريبي/sample mail.mbox" REPORT_DIR="$(OUT_DIR)/space path report"
	REPORT_FILE="$(OUT_DIR)/space path report/applications.csv" $(PYTHON) -c 'import csv, os; rows=list(csv.DictReader(open(os.environ["REPORT_FILE"], encoding="utf-8-sig"))); assert len(rows) == 3, len(rows); print("path-smoke rows:", len(rows))'

agent-check:
	$(MAKE) check
	$(MAKE) demo
	$(MAKE) path-smoke
	$(MAKE) package

package:
	/bin/rm -rf dist build *.egg-info
	$(PYTHON) -m build
	$(PYTHON) -m twine check dist/*

publish:
	@if /bin/test -z "$$TWINE_USERNAME" -o -z "$$TWINE_PASSWORD"; then \
		/bin/echo 'missing PyPI credentials. Set TWINE_USERNAME=__token__ and TWINE_PASSWORD=pypi-...'; \
		exit 2; \
	fi
	$(MAKE) package
	$(PYTHON) -m twine upload dist/*

clean:
	/bin/rm -rf $(OUT_DIR) $(REPORT_DIR) dist build *.egg-info __pycache__ tests/__pycache__
