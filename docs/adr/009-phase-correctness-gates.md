# ADR-009: Preserve correctness across roadmap phases

Status: accepted

## Decision

Bring prerequisite invariants into the first live workflow: inbox in Phase 06, tokens/i18n before screens, tests per phase and security before public deployment.

## Reason

A numbered hardening phase must not authorize an unsafe earlier implementation.

## Tradeoff and consequence

Phases 07, 16–19 and 22 deepen earlier guarantees rather than introducing them for the first time.
