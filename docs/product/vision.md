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

Omnira is a **commerce operations control plane and inventory orchestration platform**
under active development as a production-grade commercial product.

Its long-term operational loop is **Observe → Explain → Simulate → Repair → Verify**:
make commerce behavior observable, explainable, safely simulatable, repairable and
verifiable. Trust and production-quality implementation guide each incremental scope.

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

Omnira is being built for real commercial use by growing commerce teams.
Implemented subsystems must meet production engineering standards for their current
scope; unimplemented capabilities remain explicitly planned. This does not mean the
entire platform is ready for unrestricted merchant Production use.

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

## Product environments and commercial evolution

Omnira Sandbox and Commercial / Production use the same core product.

> The Sandbox is not a simplified implementation of Omnira. It is a constrained
> environment, entitlement profile, data profile, and infrastructure profile of
> the same core product.

Core domain, service architecture, event architecture and implemented correctness
guarantees remain the same. No separate repository, business-logic fork or fake
domain architecture is permitted.

## Omnira Sandbox

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
- no production SLA or HA expectations
- limited organizations, stores, users and retention
- resettable synthetic data and controlled failure scenarios

## Commercial / Production

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
- multiple inventory locations, incident response and operational dashboards
- enterprise identity and larger workloads when justified

The distinction between these states must be based on configuration, entitlements, integrations, deployment configuration, and infrastructure.

Do not create separate sandbox and commercial codebases.

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

## Environment, plan and entitlement

| Concept | Meaning | Examples |
| --- | --- | --- |
| Environment | Runtime isolation and safety policy | local, test, sandbox, staging, production |
| Plan | Commercial packaging | Free, Pro, Enterprise (illustrative, not finalized) |
| Entitlement | Capability or usage limit enforced by the application | stores.max, users.max, inventory.locations.max |

The sandbox entitlement profile limits capabilities and usage. Synthetic data,
provider allowlists, billing suppression, retention and simulator/reset enablement
are environment policies, not subscription plan names. A Free plan must not enable
Sandbox engineering controls in Production. A Shopify development store may be
explicitly allowed without allowing arbitrary merchant credentials.

Use **Omnira Sandbox** externally and **Sandbox** as the environment indicator.
Limited plans or low-cost infrastructure never weaken tenant isolation, domain
validation, idempotency or security.

## Commerce simulator

Plan a bounded Commerce Simulator / System Lab for Sandbox, integration and E2E
testing, load/failure testing and developer demonstrations. It generates synthetic
inputs through real application boundaries; it is distinct from read-only policy
simulation, which must never mutate live state.

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
- out-of-order webhooks, provider timeouts and partial synchronization
- inventory drift, unavailable warehouses and routing rule conflicts
- repair success and repair verification failure once those workflows exist

Purposes:

```text
demo
local development
integration testing
load testing
failure testing
```

Do not run the simulator in Commercial Production environments. Fail closed on
unknown environments; separate simulator credentials and control paths from
commercial runtime behavior. Never target real merchant data. Controlled reset may
reset a synthetic organization, regenerate orders, restore inventory and clear
failure scenarios; it must be scoped, authorized, auditable and denied in Production.

## System Lab / engineering demo

The Sandbox environment may later expose an engineering/demo area capable of demonstrating:

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

## Operational product loop

Omnira should help operators understand what happened across stores, inventory,
orders and integrations, why it happened, what can safely be changed and whether
the correction succeeded. This is product direction, not a claim of implemented
capabilities or market uniqueness.

```text
OBSERVE → EXPLAIN → SIMULATE → REPAIR → VERIFY → OBSERVE
```

> Technical observability becomes a product feature only when it helps an operator
> understand and control commerce behavior.

Trace IDs, events and queues support that value; they are not sufficient by themselves.

### Observe and explain

Observations combine provider webhooks, domain/integration events, orders, inventory,
reservations, sync jobs, reconciliation, audit, traces, retries and DLQ state. They
should answer what happened, when, to which entity, who or which system initiated it,
what changed and which operation caused the next one.

**Causal Operations / Causal Operational Graph** is a working capability name. A
bounded operation graph links recorded causes, such as order received → reservation
requested → location evaluated → routing rule excluded Warsaw → Berlin selected →
reservation succeeded → order confirmed. Do not infer causation from timing alone.

Explanations must distinguish recorded fact, derived deterministic explanation and
optional AI-assisted interpretation. A merchant might see “Reservation failed because
Warsaw has insufficient available stock.” An alternative location is suggested only
if recorded availability and routing constraints support it, with freshness shown.
Event/trace/correlation/causation IDs, producer, routing key, attempt number, redacted
payload and resource references belong behind authorized advanced details.

### Simulate

Eventually evaluate a specific proposed allocation, warehouse priority, routing,
safety-stock, automation, sync-policy or repair change without applying it. Report
current state, proposed change, predicted result, affected resources and risks.
Comparisons may include fulfillable orders, split shipments, stock conflicts and
location workload, but only when the underlying model supports those measures.

Use deterministic, bounded evaluators for implemented operations. Historical orders,
events, provider records and inventory snapshots may supply inputs only when retained
and sufficiently complete. Missing data limits the result; no generalized simulation
or rule engine is required early.

### Repair and verify

> Every future remediation capability should prefer normal domain operations over
> direct state mutation.

Candidate actions include retrying reservations or sync jobs, rerouting fulfillment,
resyncing products/inventory, replaying webhooks or failed events, and correcting
provider inventory. Each becomes available only when its owner implements safe,
authorized, auditable, observable behavior and appropriate retry/idempotency rules.
Direct administrative state mutation is exceptional and strongly controlled.

Non-trivial repairs need a plan describing evidence, proposed and approved changes,
constraints, affected orders/resources, expected outcomes and verification. For
example, correcting provider stock from 12 to authoritative stock 9 must preserve
existing reservations and then request a verification fetch/reconciliation. A command
being accepted is not proof of correction. Conceptual states are proposed, approved,
executing, awaiting_verification, verified and failed; models are deferred.

Risk concepts are read_only, safe_retry, bounded_mutation and high_impact_mutation.
An idempotent replay may be safe_retry; a provider quantity correction may be a bounded
mutation; a bulk reroute may be high impact. Classification is operation-specific.
Organization, role, ownership, risk and approval policy govern authorization. A future
policy could deny VIEWER repair, permit OPERATOR approved low-risk work, let ADMIN
approve larger repairs and OWNER configure automation; this mapping is not finalized.

### Operations workspace and historical state

Operations should eventually bring together active incidents, integration/sync
failures, DLQ items, drift, blocked orders, repair suggestions, recent repairs and
verification failures. The Operational Timeline remains the entry point into
chronology, cause, related entities, explanations, advanced details, supported repair
actions and verification results. Introduce each only with real supporting behavior.

**Commerce Time Machine** is a working name for historical inspection around an
order, SKU, product, store, location, sync job or integration. Show known physical,
reserved, available and provider quantities alongside transitions, observations and
gaps. Events, audit records, snapshots, historical records and projections may combine;
Omnira does not claim full event sourcing or arbitrary point-in-time reconstruction.

### Policy-driven self-healing and optional AI

Future policies may offer observe_only, suggest, require_approval and auto_repair.
Automatic action applies only to explicitly safe allowlisted scenarios within limits,
such as bounded inventory drift, and must still authorize, audit and verify. Never
automatically repair arbitrary failures.

AI may later help wording, incident summaries, investigation paths or history queries.
Deterministic business state remains authoritative; AI must not invent state, become a
correctness dependency or execute high-impact repairs without application policy and
authorization. All explanation, risk, incident and repair text follows existing i18n;
stable reason codes with structured metadata drive behavior, never log-string matching.

## Trust and production-first delivery

Trust is a product requirement: correctness, tenant isolation, authorization,
auditability, safe mutations, recoverability, deterministic behavior, migration safety,
provider consistency and failure visibility take precedence over impressive shortcuts.
Production quality is appropriate engineering at the current scale, not premature HA
or enterprise infrastructure. Temporary code needs explicit scope, a replacement
condition and a reason it is safer/cheaper than abstraction; it cannot weaken security
or correctness. A feature can be absent; it must not be deliberately second quality.

Every substantial subsystem addresses relevant failures, bounded work, safe lifecycle,
data/API contracts, security and useful observability as it is implemented. Later
hardening phases review the whole system. Before merchant launch, a dedicated readiness
review must establish security, data integrity, backup/restore, migrations, observability,
incident handling, provider failures, rate limits, load behavior, deployment/rollback,
credential protection, privacy and compliance requirements and support procedures.
