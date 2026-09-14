# Omnira

Omnira is a commerce operations and inventory orchestration platform designed to
centralize orders, inventory, integrations, and operational workflows across commerce
channels. It is Shopify-first, with provider-independent domain boundaries.

The preview and future commercial product share one implementation. Configuration,
entitlements, integrations and infrastructure determine the deployment profile.

## Status

Foundation planning and repository checks are available. Application services,
frontend runtime, infrastructure Compose configuration and deployment are not yet
implemented. No production capability is implied by the target architecture.

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
scans the Git index and available history. No application build command exists yet.

The intended stack is Go/Gin, PostgreSQL with pgx/sqlc/goose, RabbitMQ, Redis,
Next.js/TypeScript and NestJS notifications. Modules and infrastructure are added
incrementally when their responsibilities exist.
