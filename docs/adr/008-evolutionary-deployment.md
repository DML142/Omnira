# ADR-008: Evolve deployment when evidence requires it

Status: accepted

## Decision

Begin with Compose and privately reachable service infrastructure. Caddy/Gateway provides standard public API ingress; managed providers remain replaceable.

## Reason

Cost-constrained sandbox must preserve production boundaries.

## Tradeoff and consequence

HA, Kubernetes, sharding and service mesh require evidence and further ADRs; no initial HA claim.
