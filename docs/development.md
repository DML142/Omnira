# Development workflow

## Runtime baseline

Phase 00 provides a Go/Gin Gateway with liveness and graceful shutdown, a minimal
Next.js web application, and local PostgreSQL/RabbitMQ/Redis infrastructure. No
identity, commerce workflow, database application schema or provider integration
exists yet. The Gateway does not connect to storage just to report process liveness.

## Prerequisites and versions

- Git, Make, Python 3.10+ and a C compiler for Go race tests.
- Go 1.27.1, pinned in `.go-version`, `go.work` and the Gateway module. Make uses
  `GOTOOLCHAIN` to select/download it; an existing Go 1.21+ can bootstrap the toolchain.
- Node 24.21.0 LTS with npm 11.19.0, pinned in `.node-version`, `.nvmrc` and web engines.
  With nvm installed, run `nvm install` then `nvm use` in the repository root.
- Docker Engine/Desktop and Compose v2.34.0 or newer; the selected Docker context
  must be running and accessible to your user. Check `docker info` before startup.
- Gitleaks 8.24.3. Install with
  `go install github.com/zricethezav/gitleaks/v8@v8.24.3` and add the Go bin directory
  to PATH. CI pins the same version.

Gin is pinned in `services/gateway/go.mod`; web dependencies are exact versions with
an npm lockfile. `make tools` installs golangci-lint 2.13.2 into ignored `bin/`.
Review dependency/toolchain updates deliberately; pinning does not replace updates.
ESLint 10 uses the Next.js plugin directly, TypeScript rules and React Hooks rules.
The aggregate Next.js ESLint preset currently brings React/accessibility/import
plugins that reject ESLint 10; the foundation avoids those incompatible dependencies
and the EOL ESLint 9 runtime. Browser keyboard/contrast checks cover this minimal UI;
add a compatible accessibility ruleset when expanding the frontend. See
[ESLint support](https://eslint.org/version-support/) and
[Next.js plugin configuration](https://nextjs.org/docs/app/api-reference/config/eslint).
Version selection references: [Go releases](https://go.dev/dl/),
[Node release support](https://nodejs.org/en/about/previous-releases), and
[Next.js installation](https://nextjs.org/docs/app/getting-started/installation).

## First local startup

From the repository root after selecting the pinned Node version:

```sh
make setup
npm --prefix apps/web ci
make infra-up
make gateway
```

In another terminal, from the same root and Node environment:

```sh
make web
```

Open `http://127.0.0.1:3000` for the minimal web page; Gateway liveness is
`http://127.0.0.1:8080/healthz` and returns `{"status":"ok"}`. The web page does not
claim database, broker or business-service readiness. It makes no backend requests.
No authentication exists, so this baseline is local-only, not a public sandbox.

Gateway reads optional `OMNIRA_GATEWAY_ADDR` directly from the process environment.
It defaults to `127.0.0.1:8080`; override with, for example,
`OMNIRA_GATEWAY_ADDR=127.0.0.1:8081 make gateway`. The address must be a numeric loopback IP
and a port from 1 to 65535. `.env` is read by Compose, not automatically by Gateway.
Only `/healthz` is implemented; unknown paths and unsupported methods return JSON
error codes. SIGINT/SIGTERM drains active requests for up to 10 seconds, then closes
connections and exits with failure if the drain deadline was exceeded.

For the built web application, run `npm --prefix apps/web run build` followed by
`npm --prefix apps/web start`. For the compiled Gateway use `bin/gateway` after
`make check-go`; sending SIGTERM to that process exercises graceful shutdown directly.
Use Ctrl+C to stop foreground development processes. `make infra-down` removes
Compose containers/network while preserving the named data volumes.

## Credentials and infrastructure

`make setup` generates unique random credentials into ignored `.env` with mode 0600.
It never overwrites an existing file or prints its credentials. The public
`config/environment.example` contains blank password fields; Compose rejects missing
credentials. Do not run `docker compose config` without `--quiet` in shared logs,
since expanded configuration includes environment credentials.

Only local infrastructure administrators use the initial `omnira` database/broker
account. PostgreSQL owns database `omnira`; application-specific schemas and restricted
roles arrive with the owning services. Gateway has no database credentials or access.
Redis requires a password and uses AOF persistence; it remains disposable infrastructure,
not a business source of truth. Its password must be at least 32 hexadecimal characters;
`make setup` generates 64. Service credentials are visible to local Docker administrators.

| Service | Host address | Data volume |
| --- | --- | --- |
| PostgreSQL | 127.0.0.1:5432 | postgres_data |
| RabbitMQ AMQP | 127.0.0.1:5672 | rabbitmq_data |
| RabbitMQ management | 127.0.0.1:15672 | rabbitmq_data |
| Redis | 127.0.0.1:6379 | redis_data |

Change the corresponding `*_PORT` variables in `.env` if a port is already occupied.
Every published infrastructure port remains bound to loopback. Compose prefixes
volumes with its project name, normally `omnira`.

PostgreSQL and RabbitMQ initialize accounts only when their volumes are empty.
Editing `.env` alone does not rotate credentials in existing volumes. Keep `.env`
with its local data; rotate through the service tools when preserving data matters.
For disposable data only, `docker compose down --volumes` deletes this project's
stored data, after which a fresh `.env` and `make infra-up` can initialize new accounts.
Do not use that command against data you need. Never prune unrelated Docker resources.

## Verification

```sh
make check
make check-local
make check-go
make check-web
make check-infra
# Or all runtime suites:
make check-runtime
```

`make check-go` checks formatting, vet, race tests, golangci-lint and build, then runs
a real process health/SIGTERM smoke check. Tests cover active request draining and
forced closure at the shutdown deadline. `make check-web` runs ESLint, TypeScript
and production build separately; typecheck generates route declarations first.
Next.js build is not a replacement for lint.

`make check-infra` creates a random Compose project with temporary credentials and
random loopback ports. It validates missing credentials, health checks and port scope,
then performs authenticated probes and verifies PostgreSQL data, Redis AOF data and
a durable RabbitMQ message survive container recreation. It removes only its own
containers, volumes and network and verifies teardown. It requires real Docker;
unavailable infrastructure is a failed check, never a mocked pass.

CI runs repository/secret checks, Gateway, web and infrastructure jobs separately.
It does not require private `.ai` files. Local commands mirror these jobs; remote
workflow success must be verified after an authorized push.

## Repository checks and secret protection

```sh
make hooks
# After staging only reviewed public files:
make secrets
```

`make check` validates links, whitespace and protected tracked paths. `make secrets`
scans the full staged tree and all locally available Git history. It does not scan
unstaged changes; stage the exact reviewed candidate and rerun before committing.
The pre-commit hook scans the staged patch and fails if the scanner is absent.
The ignore rules cover `.env`, `.env.*`, secret directories, PEM/key files and private
orchestration. Never force-add ignored material.

A clean clone can run the public application and checks using this guide. Before
further automated source work, the maintainer must separately restore private `.ai`
project memory from their trusted local copy and run `make check-local`; that state
is intentionally absent from Git and must not be invented from public documentation.

## Git workflow and definition of done

Use feature/<feature>, fix/<issue>, refactor/<area> or chore/<maintenance>, with one
coherent feature per branch and small Conventional Commits. Main is the integration
branch. Do not merge, push or deploy without authorization. Require CI on main when
host settings are configured; scripts cannot enforce remote branch protection.

Completion requires relevant tests/lint/typecheck/build/integration checks, reviewed
errors/security/observability, synchronized docs and execution state, clean diff and
secret scan, and a logical commit. Unavailable checks mean partial completion.
Tenant authorization, owner-specific database tests and Testcontainers are added with
the first relevant business modules; no empty services exist to satisfy a diagram.
