.PHONY: check check-local secrets hooks

check:
	python3 scripts/check_repository.py
	git diff --check
	git diff --cached --check

check-local:
	python3 scripts/check_local_state.py

secrets:
	sh scripts/scan_secrets.sh

hooks:
	git config core.hooksPath .githooks
