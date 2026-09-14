# ADR-006: Keep commerce providers outside core domains

Status: accepted

## Decision

Integrations owns stores, credentials, raw ingress and mappings. Normalize mock/Shopify models into versioned Omnira contracts.

## Reason

Provider API evolution must not redefine Orders or Inventory.

## Tradeoff and consequence

Mapping and reconciliation logic live at the adapter boundary; provider IDs remain external mapping fields.
