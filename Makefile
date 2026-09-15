GO_VERSION := $(shell cat .go-version)
GO := GOTOOLCHAIN=go$(GO_VERSION) go
GOLANGCI_VERSION := v2.13.2

.PHONY: check check-local secrets hooks setup tools check-go check-web check-infra check-runtime gateway web infra-up infra-down

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

setup:
	python3 scripts/setup_local.py

bin/golangci-lint:
	GOBIN=$(CURDIR)/bin $(GO) install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@$(GOLANGCI_VERSION)

tools: bin/golangci-lint
	bin/golangci-lint version | grep -F "version $(GOLANGCI_VERSION:v%=%) "

check-go: tools
	@go_root=$$($(GO) env GOROOT) && files=$$("$$go_root/bin/gofmt" -l services/gateway) && \
	  { test -z "$$files" || { printf 'Format these files:\n%s\n' "$$files"; exit 1; }; }
	$(GO) vet ./services/gateway/...
	$(GO) test -race ./services/gateway/...
	bin/golangci-lint run ./services/gateway/...
	$(GO) build -o bin/gateway ./services/gateway/cmd/api
	python3 scripts/check_gateway.py

check-web:
	npm --prefix apps/web run lint
	npm --prefix apps/web run typecheck
	npm --prefix apps/web run build

check-infra:
	python3 scripts/check_infra.py

check-runtime: check-go check-web check-infra

gateway:
	$(GO) run ./services/gateway/cmd/api

web:
	npm --prefix apps/web run dev

infra-up:
	docker compose up -d --wait --wait-timeout 180

infra-down:
	docker compose down
