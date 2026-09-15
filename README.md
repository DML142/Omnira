# Omnira

Omnira is a commerce operations and inventory orchestration platform designed to
centralize orders, inventory, integrations, and operational workflows across commerce
channels. It is Shopify-first, with provider-independent domain boundaries.

The preview and future commercial product share one implementation. Configuration,
entitlements, integrations and infrastructure determine the deployment profile.

## Status

Phase 00 runtime foundation is available: a minimal Go/Gin Gateway, Next.js web
bootstrap, local PostgreSQL/RabbitMQ/Redis Compose services, and executable checks.
Identity, business services, provider integrations and deployment are not implemented.
The target architecture is not a claim of production readiness.

## Local startup

Use the pinned toolchains and Docker prerequisites in the
[development guide](docs/development.md), then run:

```sh
make setup
npm --prefix apps/web ci
make infra-up
make gateway
# In a second terminal:
make web
```

Web: `http://127.0.0.1:3000`. Gateway liveness: `http://127.0.0.1:8080/healthz`.
Stop infrastructure with `make infra-down`; data volumes are preserved.

## Documentation

- [Product vision and vocabulary](docs/product/vision.md)
- [System architecture and ownership](docs/architecture/system.md)
- [System diagram](docs/diagrams/system.md)
- [Design system](docs/product/design.md)
- [Architectural decisions](docs/adr/README.md)
- [Development workflow](docs/development.md)
- [Security and operational baseline](docs/security.md)

## Repository checks

Install Python 3, Git, Make and the Gitleaks version documented in the development
guide. Run `make check` for public repository checks and `make hooks` to enable the
local pre-commit protection. Stage reviewed public files before `make secrets`, which
scans the Git index and available history. Run `make check-runtime` for Gateway,
web and real infrastructure validation.

The planned full stack is Go/Gin, PostgreSQL with pgx/sqlc/goose, RabbitMQ, Redis,
Next.js/TypeScript and NestJS notifications. Modules and infrastructure are added
incrementally when their responsibilities exist.
