# ADR-010: Keep initial operational projections with existing owners

Status: accepted

## Decision

Orders owns its timeline; Integrations owns integration failure views; each service owns its audit entries. Gateway composes APIs.

## Reason

An operations view does not yet justify a new service or cross-service database joins.

## Tradeoff and consequence

Projection lag and partial reads must be visible; future extraction requires evidence and a migration ADR.
