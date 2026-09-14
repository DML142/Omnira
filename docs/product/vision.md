# Product definition

Status: approved product direction; planned capabilities are not implemented.

## Target user

Operations leads and operators at growing commerce brands managing multiple stores,
stock locations, order exceptions, and unreliable integration workflows. Engineering
and support teams need traceable failures and safe recovery rather than database access.

## Core problems

Fragmented order visibility, overselling, provider-specific workflows, silent sync
failures, and difficult incident recovery. Success means operators can identify an
exception, understand its cause, and safely resolve it within their organization.

## Product vision

Omnira is a **commerce operations and orchestration platform**.

It should initially be Shopify-first but must never become tightly coupled to Shopify at the domain level.

Omnira is not a Shopify clone.

Shopify remains responsible for areas such as:

- storefront
- checkout
- payment processing
- commerce primitives
- basic catalog functionality

Omnira acts as an operational control layer above Shopify and potentially other commerce systems.

The long-term product direction includes:

- multi-store operations
- centralized orders
- centralized inventory
- inventory reservation
- warehouse/location inventory
- multi-channel synchronization
- external integration reliability
- operational timelines
- failed sync visibility
- webhook processing
- retries
- DLQ inspection
- event replay
- reconciliation
- audit logs
- workflow automation
- operational alerts
- commerce observability
- analytics
- future public APIs
- future developer integrations
- billing and entitlements

Omnira should eventually be capable of becoming a real commercial SaaS product used by growing e-commerce companies.

## Product positioning

Omnira should be positioned approximately as:

> Commerce operations and inventory orchestration for Shopify brands.

or:

> An operational control plane for growing commerce businesses.

The product must complement Shopify rather than compete with it directly.

The architecture must support future providers such as:

- Shopify
- WooCommerce
- Amazon
- Etsy
- custom storefronts
- custom ERP systems
- warehouse systems
- fulfillment providers

However, only Shopify and a mock provider are relevant to the early roadmap.

Do not prematurely implement other providers.

## Product states

The same codebase must support two main product states.

## Portfolio / Preview

Typical characteristics:

- public demo
- synthetic data
- mock commerce provider
- optional real Shopify developer-store integration
- one demo organization
- strict usage limits
- billing disabled
- email delivery disabled or reduced
- low-cost infrastructure
- demo simulator
- public read-only or limited demo user
- no enterprise features
- no production HA requirements

## Commercial

Future characteristics:

- real organizations
- real stores
- real Shopify installations
- multiple stores per organization
- billing
- entitlements
- usage limits
- encrypted integration credentials
- backups
- production observability
- production support tooling
- real email and notifications
- HA infrastructure where necessary
- increased retention
- multiple deployment environments
- stronger infrastructure isolation

The distinction between these states must be based on configuration, entitlements, integrations, deployment configuration, and infrastructure.

Do not create separate portfolio and commercial codebases.

## Core product concepts

The system should eventually support:

- User
- Identity
- Session
- Organization
- Membership
- Role
- Store
- Commerce Provider
- Product
- Product Variant
- SKU
- Inventory Location
- Stock Level
- Stock Reservation
- Order
- Order Item
- Integration
- Webhook Delivery
- External Event
- Sync Job
- Notification
- Audit Entry
- Operational Event
- Entitlement
- Subscription
- Automation Rule
- Workflow Trigger
- Workflow Condition
- Workflow Action

Not all of these should be implemented immediately.

They are architectural concepts for the long-term design.

## Primary business flow

A representative future order flow:

```text
Shopify
   ↓
Webhook Ingress
   ↓
signature validation
   ↓
deduplication
   ↓
raw event persistence
   ↓
fast acknowledgement
   ↓
asynchronous processing
   ↓
normalization
   ↓
Omnira event
   ↓
Orders Service
   ↓
transaction + outbox
   ↓
RabbitMQ
   ↓
Inventory Service
   ↓
inventory reservation
   ↓
RabbitMQ
   ↓
Orders Service
   ↓
order confirmed / rejected
   ↓
Notifications / Integrations / Operational Timeline
```

The architecture should make this flow observable and recoverable.

## Reconciliation

Webhooks provide speed.

Reconciliation provides correctness.

Do not rely only on webhooks.

Future integrations should support:

```text
realtime webhook flow
+
scheduled reconciliation flow
```

Initial or large synchronization may later use provider bulk APIs where appropriate.

Do not implement this too early, but preserve the architecture for it.

## Multi-store model

An organization may own multiple stores.

Example:

```text
Organization
 ├── US Store
 ├── EU Store
 └── Wholesale Store
```

Each store may have:

```text
provider
credentials
sync configuration
external identifiers
status
```

This is important for long-term multi-store operations.

## Future automation engine

Long term, Omnira may support simple workflow automation:

```text
Trigger
Condition
Action
```

Examples:

```text
WHEN inventory.available < 5
THEN send alert
```

```text
WHEN order.created
IF order.total > threshold
THEN require review
```

Do not implement this in initial phases.

The architecture should allow a future automation bounded context.

## Future billing and entitlements

Commercial Omnira will require:

```text
plans
subscriptions
usage
entitlements
```

Business logic must not be hardcoded as:

```text
if plan == PRO
```

Prefer capability-oriented checks such as:

```text
multi_store
orders.month.max
users.max
inventory.locations.max
automation.rules.max
```

The exact billing implementation is future work.

Preserve a path toward a dedicated Billing / Entitlements service.

## Portfolio edition as entitlements

Portfolio mode should be expressible conceptually through limits such as:

```text
stores.max = 1
users.max = 1
real_integrations = false
synthetic_data = true
billing = false
```

Do not build a separate portfolio product.

## Commerce simulator

Plan a small internal/demo simulator for future use.

Potential path:

```text
tools/simulator/
```

The simulator may eventually generate:

- orders
- inventory changes
- webhook events
- duplicate messages
- failures
- delayed events
- sync failures

Purposes:

```text
demo
local development
integration testing
load testing
failure testing
```

Do not run the simulator in commercial production environments.

## System Lab / engineering demo

Portfolio mode may later expose an engineering/demo area capable of demonstrating:

```text
duplicate event
consumer failure
delayed processing
inventory race
DLQ
replay
trace flow
```

This is a future feature.

Do not build it early.

## Non-goals

No storefront, checkout, payment processor, ERP replacement, or Shopify clone.
No providers beyond mock and Shopify in the early roadmap. No premature automation,
billing, analytics platform, public developer API, or enterprise infrastructure.

## Product vocabulary

| Term | Meaning |
| --- | --- |
| Organization | Tenant and authorization boundary |
| Store | Organization-owned connection to a commerce channel |
| Provider | External commerce system behind an adapter |
| Integration | Provider connectivity, credentials, and synchronization state |
| SKU | Business stock identifier; never a globally unique tenant identity |
| Location | Physical or logical inventory holding location |
| Reservation | Transactional claim against available stock for an order |
| Operational event | Business-readable workflow observation |
| Audit entry | Attributable record of a user or administrative action |
| Replay | Authorized reprocessing with idempotency and recorded provenance |
| Entitlement | Capability or usage limit, independent of billing plan names |
