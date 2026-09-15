# ADR-011: Extend operational insight and recovery within existing boundaries

Status: accepted direction; capabilities remain planned

## Context and impact assessment

The product direction expands from operational chronology to Observe → Explain →
Simulate → Repair → Verify. Phase 00 is complete; business workflows remain planned.
ADRs 001–010 already establish the necessary ownership, provider, event, correctness,
projection, design and deployment foundations. None is superseded by this extension.

## Decision

Build causal and historical views from owner-local operational events, audit/history,
versioned transitions, snapshots and projections as concrete workflows require them.
Preserve the envelope and transport trace separation; add compatible metadata only
for demonstrated needs. Explain from recorded facts and deterministic reason codes,
with optional AI interpretation clearly separated and never authoritative.

Use bounded deterministic simulations with explicit input coverage and no live effects.
Repairs use normal owner application/domain operations with risk-aware authorization,
plans where needed, audit, idempotency and independently observed verification. A future
cross-owner plan needs an explicit orchestration owner; Gateway remains API composition.
Policy-driven automatic repair is a later, allowlisted, bounded extension of this path.

Operations, remediation, automation and analytics are possible contexts within existing
services first. No new service, event-sourcing conversion, graph/vector database,
workflow platform or other infrastructure is warranted solely by this product vision.

Omnira Sandbox is the constrained environment of the same commercial product, preserving
implemented correctness. Environment, plan and entitlement remain distinct. Simulator
failure injection and reset controls are isolated from Production. Production engineering
quality applies to every implemented scope; merchant launch requires a separate evidence-
based readiness review. Future UI appears only with meaningful supported behavior.

## Tradeoff and consequence

Historical coverage depends on deliberate retention and snapshots; do not promise exact
arbitrary past state. Projection lag, missing causal evidence, uncertain provider writes
and failed verification must remain visible. Generic engines and service extraction are
deferred until requirements justify their cost. Existing replay keeps its original
idempotency/provenance semantics; simulation never replays into live consumers.

Roadmap work follows real orders/inventory/integrations, events and timeline, then causal
reliability, Operations, Explain, bounded simulation, repair with minimum verification,
expanded verification, historical inspection and policy-driven remediation. This ADR
changes planning only and does not reopen Phase 00 or activate another phase.
