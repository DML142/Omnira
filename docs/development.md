# Development workflow

## Current baseline

The repository contains product and architecture definitions, design requirements,
ADRs, and executable repository checks. Runtime foundation is outstanding: minimal
Go/Gin health service, go.work, Next.js bootstrap, local Compose infrastructure and
the corresponding compile/lint/test jobs. Add real modules only; no empty service
skeletons or business features belong in the foundation increment.

## Checks and secret protection

Prerequisites: Python 3.10+, Git, Make and Gitleaks 8.24.3. Install the scanner from
its [official release](https://github.com/gitleaks/gitleaks/releases/tag/v8.24.3), or
use Go with `go install github.com/zricethezav/gitleaks/v8@v8.24.3` and put the Go bin
directory on PATH. CI uses this exact version. Review scanner/toolchain updates as
maintenance changes; pinned does not mean permanently current.

```sh
make check
make hooks
# After staging only reviewed public files:
make secrets
```

`make check` validates links, whitespace and protected tracked paths. `make secrets`
scans the full staged tree and all locally available Git history. It does not scan
unstaged changes; stage the exact reviewed candidate and rerun before committing.
The pre-commit hook scans the staged patch and fails if the scanner is absent.
CI fetches full history and scans the public checkout; it requires no local project
memory. `make check-local` is a separate maintainer check for private execution state.

The ignore rules cover .env, every .env.* file, secrets directories, PEM/key files,
and private orchestration. Use config/environment.example for tracked placeholders;
copy it to .env only when needed. Do not weaken protection to commit an example.
A fresh clone requires restoring private execution state before automated source
work; public architecture describes the product but does not select the next task.

## Git workflow

Main is the integration branch. Use feature/<feature>, fix/<issue>, refactor/<area>
or chore/<maintenance>. Work on one coherent feature per branch and normally open
one PR per completed feature. Use small Conventional Commits, for example
`chore(repo): establish engineering foundations`. Never force-add ignored material.

A PR describes the problem, changed behavior and validation concisely. Review the
diff for secrets, tenant scope, error behavior, architectural changes and unrelated
work. Do not merge or deploy merely because a local commit exists. Require CI on
main when the remote is configured; repository scripts cannot enforce host settings.

## Definition of done

Required implementation is complete; relevant tests, lint, typecheck and integration
checks pass; tenant/security behavior and error handling are verified; observability
is considered; docs and execution state agree; diff and secret scan are clean; a
logical commit exists. Unavailable checks or incomplete acceptance criteria mean
partial work, never completion.

Add Go formatting, vet, golangci-lint, unit/integration tests and builds alongside
actual modules. Add frontend lint, typecheck, tests and build alongside the web app.
Use Testcontainers for real database and broker guarantees. Keep fast PR checks and
heavy release suites separate without skipping required correctness coverage.
