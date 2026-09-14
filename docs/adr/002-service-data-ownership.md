# ADR-002: Services own their data

Status: accepted

## Decision

Start with owner-restricted PostgreSQL schemas and roles; prohibit cross-service SQL and shared business models. Organization scopes every tenant resource.

## Reason

Independent evolution and tenant safety require enforceable ownership.

## Tradeoff and consequence

Cross-service reads require APIs or projections; eventual consistency is explicit.
