# ADR-001: Use one implementation across product states

Status: accepted

## Decision

Omnira Sandbox is a constrained environment, entitlement, data and infrastructure
profile of the same core commercial product, preserving implemented correctness.
Environment policy and subscription plans remain separate concepts.

## Reason

Separate product forks drift and require rewrites.

## Tradeoff and consequence

Sandbox still pays the correctness cost of tenant ownership and reliable events; infrastructure and capabilities remain constrained.

## Terminology clarification

The environment previously called Portfolio / Preview is now Omnira Sandbox. This
renames the profile without changing the original one-implementation decision or
its rationale. There is no separate Sandbox business-logic fork. ADR-011 extends
this foundation with production-first operational insight and recovery requirements.
