# Technical architecture

Status: accepted target architecture. The repository contains the Phase 00 Gateway/web runtime and local infrastructure
baseline. Business services remain planned; diagrams describe intended workflows.

## Architectural invariants

One implementation serves Sandbox and Commercial / Production deployments. Organization is the
tenant boundary. Each service owns its database access. Provider schemas stop at the
Integrations adapter. Database state and outbox records commit atomically. Delivery
is at least once; consumers provide idempotent effects. Redis is disposable state.
No secrets, raw credentials, or customer payloads enter ordinary logs.

## Service architecture

Initial service boundaries:

```text
API Gateway
Identity Service
Orders Service
Catalog / Inventory Service
Integrations Service
Notifications Service
Web Application
```

Technology mapping:

```text
Gateway              Go + Gin
Identity             Go + Gin
Orders               Go + Gin
Catalog/Inventory    Go + Gin
Integrations         Go + Gin
Notifications        NestJS + TypeScript
Web                   Next.js + TypeScript
```

Do not create unnecessary services.

Do not create separate services for every table or concept.

New bounded contexts should only be extracted when product and scaling requirements justify them.

Possible future services include:

```text
billing
automation
analytics
audit
search
fulfillment
webhook-ingress
imports
exports
```

These are future possibilities, not initial implementation requirements.

## Evolutionary architecture

The system must use an evolutionary architecture.

The business architecture must be able to remain stable while infrastructure evolves.

Sandbox deployment may begin as:

```text
Vercel
+
one Linux VM
+
Docker Compose
+
managed PostgreSQL
+
managed RabbitMQ
+
managed Redis
```

A future production architecture may evolve toward:

```text
AWS ECS / EKS
RDS / Aurora
ElastiCache
Amazon MQ or another broker
S3
CloudFront
WAF
Secrets Manager
EventBridge
multiple environments
multiple replicas
```

The core domain and service boundaries should not require a rewrite when infrastructure changes.

Do not build Kubernetes, Kafka, service mesh, or enterprise infrastructure before it is justified.

## Go backend stack

Use:

```text
Go
Gin
PostgreSQL
pgx
sqlc
goose
RabbitMQ
amqp091-go
Redis
go-redis
OpenTelemetry
log/slog
go-playground/validator
golang-jwt/jwt
Argon2id
google/uuid or equivalent UUID library
testify
testcontainers-go
golangci-lint
```

Prefer standard library solutions when appropriate.

Avoid adding dependencies without clear value.

## Database principles

Use PostgreSQL.

Use explicit SQL.

Use:

```text
pgx
sqlc
goose
```

Do not use GORM.

Important reasons:

- explicit transactions
- explicit locking
- predictable SQL
- indexes
- constraints
- query control
- concurrency correctness
- outbox implementation
- production visibility

## Database ownership

Each service owns its own data.

Even if the Sandbox deployment uses one physical PostgreSQL cluster, services must have logical data ownership boundaries.

Example:

```text
identity
orders
inventory
integrations
```

may use separate databases or schemas.

A service must NEVER read another service's tables directly.

Forbidden example:

```sql
SELECT *
FROM inventory.stock_levels
```

inside Orders Service.

Cross-service communication must happen through:

- APIs
- asynchronous events
- projections
- explicitly defined contracts

Never create a shared application database model across services.

## Identity model

Initial concepts:

```text
User
Identity
Session
Organization
Membership
Role
```

Do not design User as inherently password-only.

Authentication may begin with:

```text
email/password
JWT
refresh sessions
```

Future architecture must allow:

```text
Google
Shopify identity
OIDC
SAML
SCIM
```

Roles initially:

```text
OWNER
ADMIN
OPERATOR
VIEWER
```

Organization is the primary tenant boundary.

## Tenant isolation

Tenant isolation is a critical architectural invariant.

Every tenant-owned resource must belong to an organization.

All relevant operations must enforce:

```text
organization_id
```

Never rely only on opaque resource IDs.

Integration tests must explicitly verify that one organization cannot access another organization's:

- orders
- products
- inventory
- stores
- integrations
- operational events
- audit entries

## Orders Service

Orders Service owns:

```text
orders
order_items
order_status_history
outbox_events
inbox_events
```

Possible order states:

```text
PENDING
AWAITING_INVENTORY
CONFIRMED
REJECTED
CANCELLED
FULFILLED
```

Order item data should contain useful immutable snapshots such as:

```text
sku
product_name
quantity
unit_price
```

Orders Service must not depend on live Product or Inventory database reads for historical display.

## Catalog / Inventory Service

Initial ownership:

```text
products
variants
inventory_locations
stock_levels
stock_reservations
outbox_events
inbox_events
```

Core inventory concepts:

```text
physical
reserved
available
allocated
safety_stock
```

Do not implement all future inventory concepts immediately.

Start with a correct reservation model.

## Inventory concurrency

Inventory reservation must be concurrency safe.

A mandatory future test case:

```text
stock = 1

Order A requests 1
Order B requests 1

both execute concurrently
```

Expected result:

```text
exactly one reservation succeeds
exactly one fails
stock never becomes negative
```

Use proper transactions and locking.

Do not solve this only in application memory.

## Integrations Service

Integrations Service owns provider connectivity.

Initial providers:

```text
mock
shopify
```

Use an anti-corruption layer.

External provider models must NEVER become Omnira domain models.

Flow:

```text
Shopify model
    ↓
provider adapter
    ↓
normalization
    ↓
Omnira domain model
```

Orders Service must not know about Shopify-specific schemas.

Inventory Service must not know about Shopify-specific schemas.

## Shopify integration architecture

Shopify must be treated as a first-class integration, not the domain itself.

Suggested structure:

```text
providers/
  shopify/
    auth/
    adminapi/
    webhooks/
    orders/
    products/
    inventory/
    mapper/
```

Shopify API version must be explicit configuration.

External API version compatibility must be considered.

Do not hardcode assumptions that a provider schema will never change.

## Webhook ingress

Webhook handling must be designed as a fast ingress pipeline.

Do not execute a large business workflow inside the webhook HTTP request.

Desired flow:

```text
webhook received
↓
validate signature
↓
deduplicate
↓
persist raw event
↓
acknowledge provider
↓
process asynchronously
```

Store raw external event information such as:

```text
id
provider
external_event_id
store_id
topic
provider_api_version
payload
received_at
processed_at
status
error
```

This enables:

- debugging
- retries
- support
- replay
- mapper fixes
- forensic analysis

## Internal and external IDs

Never use external provider IDs as Omnira primary identifiers.

Example:

```text
id                Omnira UUID
organization_id
store_id
provider
external_id
```

Internal relations must use Omnira IDs.

External IDs are mapping data.

## RabbitMQ

Use RabbitMQ for operational asynchronous messaging.

Use a topic exchange such as:

```text
omnira.events
```

Example routing keys:

```text
order.created.v1
order.confirmed.v1
order.rejected.v1

inventory.reservation.requested.v1
inventory.reserved.v1
inventory.reservation_failed.v1
inventory.low.v1

integration.order.received.v1
integration.sync_failed.v1
```

Possible queues:

```text
orders.events
inventory.events
integrations.events
notifications.events
```

Do not create one queue for every event type without reason.

## Event envelope

All Omnira domain/integration events must follow one consistent envelope.

Example:

```json
{
  "event_id": "uuid",
  "event_type": "inventory.reserved.v1",
  "occurred_at": "timestamp",
  "correlation_id": "uuid",
  "causation_id": "uuid",
  "producer": "inventory-service",
  "organization_id": "uuid",
  "payload": {}
}
```

Important fields:

```text
event_id
event_type
occurred_at
correlation_id
causation_id
producer
organization_id
payload
```

Event schemas must be versioned.

## Transactional outbox

Transactional outbox is mandatory.

Never perform this pattern:

```text
write database
then
publish event
```

without atomicity guarantees.

Correct pattern:

```text
BEGIN

write domain state
write outbox event

COMMIT
```

Then an outbox worker publishes pending events.

Only after successful publication should the outbox state be updated appropriately.

## Inbox and idempotency

RabbitMQ must be treated as at-least-once delivery.

Consumers must be idempotent.

Use inbox/event processing state where required.

Duplicate delivery must not create duplicate:

- reservations
- orders
- notifications
- transitions
- audit operations

A repeated event must safely become a no-op when already processed.

## Retries and DLQ

Important consumers must support:

```text
main queue
retry behavior
dead-letter queue
```

After exhausted retries, failed messages should become inspectable.

A future operations UI may expose:

```text
failed events
retry
replay
```

Do not build complex retry infrastructure prematurely, but design event processing around this requirement.

## Replay

Architecture must allow replay of:

- provider webhooks
- failed events
- DLQ messages
- synchronization jobs

Replay must be safe and must respect idempotency.

## Notifications Service

Notifications Service should use:

```text
NestJS
TypeScript
RabbitMQ consumer
```

Notifications retains its accepted NestJS/TypeScript boundary for event-driven delivery.
It must meet the same contract, lifecycle and correctness requirements as Go services.

It may consume events such as:

```text
order.confirmed.v1
order.rejected.v1
inventory.low.v1
integration.sync_failed.v1
```

Initial notification delivery can be simple.

Do not require real paid email infrastructure for early sandbox deployment.

## Redis

Redis may be used for:

- rate limiting
- temporary cache
- temporary provider state
- short-lived synchronization metadata
- distributed coordination only where necessary

Redis must not become the primary source of truth.

Do not use Redis as a substitute for correct PostgreSQL design.

## Dependency injection

Do not introduce a heavy dependency injection framework by default.

Prefer explicit composition in Go.

Example:

```text
database
↓
repository
↓
application service
↓
transport
```

Construct dependencies explicitly in the composition root.

Use interfaces where they represent actual architectural boundaries or enable meaningful testing/substitution.

Do not create interfaces for every concrete type automatically.

## Avoid architecture theater

Do not implement patterns only because they sound senior.

Do not introduce unnecessary:

```text
Manager
Provider
Factory
CommandBus
QueryBus
Mediator
RepositoryInterface
UseCaseInterface
ServiceInterface
```

layers.

Packages and abstractions must exist because they represent:

- domain boundaries
- infrastructure boundaries
- replaceable dependencies
- testable contracts
- provider boundaries

Not because a diagram says every project should have them.

## Shared code

Shared Go code must remain minimal.

Allowed examples:

```text
event envelope
shared transport headers
trace propagation helpers
event constants
small infrastructure utilities
```

Forbidden:

```text
shared business database models
shared service repositories
global domain model package
```

Avoid creating a distributed monolith.

## Observability

All backend services must support structured observability.

Use OpenTelemetry.

Support:

```text
structured logs
distributed tracing
metrics
```

Propagate trace and correlation context through:

```text
HTTP
RabbitMQ
internal service calls
```

Important identifiers:

```text
request_id
trace_id
correlation_id
causation_id
organization_id
```

Avoid leaking sensitive data into logs.

## Metrics

Possible important metrics:

```text
http_requests_total
http_request_duration_seconds
rabbitmq_messages_published_total
rabbitmq_messages_consumed_total
rabbitmq_consumer_errors_total
outbox_pending_events
orders_created_total
inventory_reservation_failures_total
integration_sync_failures_total
```

Do not implement every metric immediately.

Introduce metrics alongside meaningful functionality.

## Audit logging

Architecture must support audit entries for important user and administrative actions.

Possible examples:

```text
inventory changed
order cancelled
integration connected
integration disconnected
webhook replayed
member invited
role changed
```

Audit entry concept:

```text
actor
organization
action
resource_type
resource_id
metadata
timestamp
trace_id
```

Audit is not the same thing as application logs.

## Security

Security requirements:

```text
Argon2id passwords
short-lived access tokens
refresh session rotation
secure cookie handling where applicable
tenant isolation
RBAC
input validation
rate limiting
webhook signature verification
encrypted integration credentials
secret management
secure headers
least privilege
```

Never commit secrets.

Never log access tokens, passwords, refresh tokens, provider secrets, or credentials.

## Secret abstraction

Sandbox deployment may initially use environment variables.

Architecture should allow future secret storage through systems such as:

```text
AWS Secrets Manager
```

Do not over-engineer secret interfaces unless required by the code.

Integration credentials must be encrypted at rest when provider credentials are first stored.

## Storage

Object storage should use an abstraction when genuinely required.

Likely implementation:

```text
S3-compatible object storage
```

Future commercial deployment:

```text
AWS S3
```

Do not create an abstraction before a real object storage use case exists.

## Data retention

Long-term architecture should consider retention policies for:

```text
raw webhooks
audit logs
operational events
metrics
traces
```

Do not implement complex retention infrastructure in Phase 0.

Document expected future retention responsibilities.

## Search and analytics

Do not introduce OpenSearch/Elasticsearch early.

Begin with PostgreSQL where sufficient.

If search later becomes a dedicated projection, it should consume service events rather than directly coupling all databases.

Analytics should eventually favor projections/read models rather than expensive cross-service operational joins.

Do not implement analytics infrastructure prematurely.

## CQRS policy

Use CQRS concepts only where useful.

It is acceptable to have:

```text
write models
events
read projections
```

Do not create ceremonial:

```text
CommandBus
QueryBus
Mediator
```

for ordinary CRUD operations without a real need.

## Public API strategy

Only Gateway should be publicly exposed for standard application APIs.

Internal service endpoints should not be publicly reachable.

Possible public paths:

```text
/api/v1/*
```

Use API versioning.

A future public developer API is allowed but not part of early development.

## Rate limiting

Initial rate limiting may be simple.

Future architecture must allow rate limits by:

```text
IP
user
organization
API key
store
provider
```

Integration clients must also respect external provider limits.

## Repository structure

Use a monorepo.

Target top-level structure:

```text
omnira/
│
├── apps/
│   ├── web/
│   └── notifications/
│
├── services/
│   ├── gateway/
│   ├── identity/
│   ├── orders/
│   ├── inventory/
│   └── integrations/
│
├── pkg/
│   └── contracts/
│
├── tools/
│   └── simulator/
│
├── infra/
│   ├── docker/
│   ├── rabbitmq/
│   ├── otel/
│   └── deploy/
│
├── scripts/
│
├── docs/
│   ├── architecture/
│   ├── adr/
│   ├── product/
│   └── diagrams/
│
├── .github/
│   └── workflows/
│
├── docker-compose.yml
├── Makefile
├── go.work
├── README.md
└── .gitignore
```



## Typical Go service structure

Use a consistent structure similar to:

```text
services/orders/
├── cmd/
│   ├── api/
│   │   └── main.go
│   └── worker/
│       └── main.go
│
├── internal/
│   ├── domain/
│   ├── application/
│   ├── repository/
│   │   └── postgres/
│   ├── messaging/
│   │   └── rabbitmq/
│   ├── transport/
│   │   └── http/
│   ├── database/
│   │   ├── sql/
│   │   └── generated/
│   └── config/
│
├── migrations/
├── sqlc.yaml
├── Dockerfile
├── go.mod
└── go.sum
```

This is a guideline.

Do not create empty folders purely to satisfy the diagram.

Directories should appear when their responsibilities exist.

## Docker

Local development must eventually be able to run through Docker Compose.

Expected local infrastructure:

```text
postgres
rabbitmq
redis
gateway
identity
orders
inventory
integrations
notifications
web
otel-collector
```

Observability tools may be optional through Docker Compose profiles.

Do not require every service to exist from the first commit.

## Deployment direction

Initial sandbox deployment target:

```text
Frontend:
Vercel

PostgreSQL:
Neon or equivalent managed PostgreSQL

RabbitMQ:
CloudAMQP or equivalent

Redis:
Upstash or equivalent

Backend:
one AWS Linux VM using Docker Compose

Reverse proxy:
Caddy
```

The exact providers may change later.

The architecture must not depend on these providers at the domain level.

## Caddy

Use Caddy for simple initial reverse proxy and HTTPS unless requirements change.

External traffic should enter through the Gateway.

Internal services should remain on private networks.

## CI

Use GitHub Actions.

PR checks should gradually include:

```text
go formatting
go vet
golangci-lint
go tests
integration tests
frontend lint
frontend typecheck
frontend tests
build checks
Docker build checks
```

Do not run excessively expensive test suites unnecessarily on every trivial change.

Use sensible workflow separation.

## Testing philosophy

Prefer meaningful tests.

Use:

```text
unit tests
integration tests
end-to-end tests
```

Use Testcontainers for infrastructure integration tests.

Important integration scenarios include:

```text
PostgreSQL transactions
RabbitMQ publication
outbox processing
consumer idempotency
inventory concurrency
tenant isolation
webhook deduplication
```

Avoid mocking every dependency.

## Important end-to-end flow

A future strong E2E test should prove:

```text
create order
↓
order persisted
↓
outbox event created
↓
RabbitMQ receives event
↓
inventory reservation occurs
↓
inventory event published
↓
order becomes confirmed/rejected
↓
notification consumer receives event
```

Do not build this until relevant services exist.

## Error handling

Use structured application errors.

Backend errors should expose:

```text
machine-readable error code
safe message
optional metadata
```

Frontend should translate user-visible error messages through i18n.

Do not use backend English strings as a permanent localization mechanism.

Do not expose internal errors or secrets to clients.

## Money

Use integer minor units where applicable.

Do not use floating-point values for money.

Currency must be explicit.

Formatting belongs to locale-aware presentation logic.

## Time

Use UTC internally.

Persist UTC timestamps.

Convert only at presentation boundaries.

Use locale-aware formatting in the frontend.

## IDs

Use UUIDs consistently.

Prefer UUIDv7 where practical and supported, unless there is a documented reason otherwise.

External system IDs remain separate fields.

## Future scale philosophy

The project must be able to grow toward large workloads.

However:

> Scalability means designing boundaries and correctness that can evolve, not deploying enterprise infrastructure before users exist.

Prefer:

```text
correct service boundaries
idempotency
observability
stateless services
explicit events
database ownership
backpressure-aware consumers
safe retries
good indexes
good queries
```

over premature:

```text
Kubernetes
Kafka
sharding
multi-region
service mesh
```

## Initial ownership decisions

| Boundary | Owned state | Access contract |
| --- | --- | --- |
| Gateway | No business database | Public /api/v1; authentication context and routing |
| Identity | Users, identities, sessions, organizations, memberships, roles | Identity and membership APIs |
| Orders | Orders, snapshots, status history, inbox, outbox | Order API and versioned events |
| Inventory | Products, variants, locations, stock, reservations, inbox, outbox | Catalog/stock API and reservation events |
| Integrations | Stores, credentials, provider ID mappings, raw deliveries, external events, sync jobs, inbox, outbox | Provider-neutral connectivity API and normalized events |
| Notifications | Delivery intents, delivery results, inbox/outbox when needed | Event subscriptions and delivery adapters |

Choose separate schemas and separate restricted database roles for local PostgreSQL;
revoke cross-schema access. Separate databases remain a deployment option. Migrations
run with an owner-specific migration role; runtime roles cannot migrate or query
another owner's tables. No cross-service foreign keys. Tenant-owned unique keys
and lookups include organization scope (and store/provider scope for external IDs).

Identity owns membership truth. Gateway authenticates, but downstream services still
authorize trusted organization context and tenant-qualified resource access. Reject
client-forged internal identity headers. Internal authentication and revocation policy
must be specified and tested before service-to-service business traffic is enabled.

## Messaging correctness and ordering

Publisher workers claim bounded outbox batches with leases or SKIP LOCKED. Use durable
queues, persistent messages, mandatory routing, and publisher confirms; an unroutable
return is failure even if confirmed. Mark sent only after routing and confirmation.
A crash after publish and before marking sent causes a duplicate, never a lost event.
Consumer inbox uniqueness is scoped by consumer and event_id. Domain changes, inbox
completion, and new outbox records share one transaction. Acknowledge after commit.
Do not commit an inbox marker before the business effect. External delivery requires
a durable delivery intent plus provider idempotency where available; do not promise
exactly-once email delivery when a provider lacks that capability.

Use per-service queues bound to required topic keys on omnira.events. Retry queues
use bounded delays and dead-letter back to the owning main queue; exhausted attempts
enter that consumer's inspectable DLQ. Poison/invalid messages do not hot-loop.
Implement topology in Phase 04 and retry policy in Phase 08, with bounded prefetch,
backpressure, connection recovery, and graceful shutdown tests.

Preserve event_id for transport retries. Replay a failed original with the same ID;
a completed consumer remains a no-op. Corrected mapping of an already processed event
requires an explicit new derived event, provenance, authorization, and audit, never
blind deletion of inbox records. External deduplication uses provider, store, and
external_event_id; acknowledge a duplicate only after durable acceptance is known.
Treat raw webhook payloads as sensitive retained data, with restricted inspection.

Event causation_id is nullable for a root event; descendants reference their cause.
Keep trace context in transport headers, separate from business correlation IDs.
Consumers reject unsupported versions and validate organization context. Additive
schema changes must preserve old consumers; breaking changes get a new event version.
Use per-aggregate version/state preconditions to reject stale transitions; broker
arrival order is not business order. Cancellation releases reservations idempotently;
late success after cancellation must trigger compensation rather than confirmation.

## Reservation baseline

Phase 03 defines physical >= 0, reserved >= 0, and available = physical - reserved
with reserved <= physical. Allocated and safety stock remain future concepts.
Phase 06 atomically reserves every line or none, locking stock rows in deterministic
order. A unique organization/order reservation key prevents duplicate allocation.
Missing SKU/location or insufficient availability returns a domain failure. Retry
serialization/deadlock failures within bounded limits. Decrementing physical below
reserved is rejected or handled through an explicit later reconciliation policy.

## Projections, audit, and retention

Phase 15 places the order timeline projection in Orders and integration failure
views in Integrations; Gateway composes tenant-filtered views through APIs. There is
no cross-service SQL and no new timeline service. Each owner records audit entries
for its own sensitive mutations; Identity owns membership/session administration.
Timeline events are not audit evidence and logs are not a substitute for either.

Integrations owns raw payload retention and reconciliation cursors; each service
owns audit and operational-event retention; platform operations owns telemetry
retention. Before public deployment, document explicit retention durations, deletion,
access, backup/restore, and sensitive-data treatment. Reconciliation compares provider
snapshots using the same normalization/application contracts as webhook processing.

## Evolution and extraction

Extract billing, automation, analytics, audit, search, fulfillment, webhook ingress,
imports, or exports only when measured scaling or domain ownership demands it.
An ADR must name the boundary, contracts, migration, operational cost, and rollback.
Do not create speculative service directories or shared business models. The target
folder layout above is a destination; instantiate directories only for real work.

## Operational loop: architecture impact assessment

Observe → Explain → Simulate → Repair → Verify extends the accepted architecture;
it requires no immediate runtime, service, database or infrastructure change. Existing
RabbitMQ, structured envelopes, correlation/causation, OpenTelemetry, raw webhooks,
reconciliation, atomic outbox/inbox, idempotency, DLQ, audit, simulator and timeline
foundations provide the path. These are target business foundations, not a claim that
Phase 00 has implemented them. See ADR-011 for the extension decision.

Do not add Kafka, Temporal, Kubernetes, full event sourcing, a graph/vector database,
LLM infrastructure or new cloud services solely for this vision. PostgreSQL owner-local
records and bounded projections remain the starting point. No entire-platform event
sourcing conversion is required.

### Ownership and future contexts

Operations, remediation, automation and analytics are possible bounded contexts, not
automatic new services. Begin with modules inside existing owners. Orders retains its
timeline and order actions; Inventory owns stock/reservation decisions; Integrations
owns provider calls, sync/reconciliation and provider corrections. Gateway composes
APIs and must not acquire a business database or silently become a repair orchestrator.

For the first cross-owner repair, select the module that owns the initiating operation
and its durable plan/execution state through an ADR; it coordinates owner commands
and consumes outcomes without cross-service transactions or SQL. Each owner enforces
its own authorization, invariants and audit. Extraction needs concrete ownership,
scaling, team-boundary or operational evidence plus contracts, migration and rollback.
No repair tables or generic workflow engine are created by this documentation task.

### Causal operations and deterministic explanations

Preserve the current event envelope. event_id identifies a fact, correlation_id groups
a workflow and causation_id links the recorded initiating event (null for a root).
Correlation alone is not proof of cause. Keep trace context in transport headers;
projections may retain trace_id as a diagnostic link, independent of trace retention.
resource_id/resource_type and store_id belong in typed payloads or versioned projection
metadata when relevant, with organization_id enforced throughout. Add optional metadata
compatibly; breaking contracts require versioning, never a wholesale envelope rewrite.

Record the relevant decision outcome, inputs/version and stable reason code at the
owner when a workflow first needs them. Examples: INVENTORY_INSUFFICIENT,
PROVIDER_STATE_DIVERGED, WEBHOOK_DUPLICATE, SYNC_TIMEOUT and
ROUTING_RULE_EXCLUDED_LOCATION. Bounded structured metadata identifies quantities,
locations, constraints and source evidence; it must not contain secrets or arbitrary
sensitive payloads. Do not infer decisions by matching free-form log messages.

Owner-local operational projections can link webhooks, domain/integration events,
order/inventory/reservation transitions, sync/reconciliation, audit references, retry
and DLQ outcomes. Record occurred/observed times and applicable aggregate versions;
arrival order and timestamps do not establish a global business order. Deduplicate
projection updates and expose lag, missing parents, partial access and retention gaps.
Bound graph depth, node count, time range and API work; links cannot cross tenants.

Derived explanations reference actual facts, rule versions and freshness. Separate
recorded fact, deterministic derivation and any labeled AI-assisted interpretation.
An unknown or incomplete cause stays unknown. Re-evaluate current availability before
an action; historical evidence is not a promise of current stock. Localize reason codes
at the frontend using structured parameters; backend logic never depends on English.
AI remains optional wording/diagnostic assistance, never authoritative business state
or a bypass around repair policy, approvals and authorization.

### Safe simulation versus replay

A bounded dry-run evaluates one implemented operation against an explicit immutable
input set and proposed policy/version. Reuse deterministic domain calculations where
appropriate, with no side-effecting adapters, live publications or provider writes.
Enforce tenant/resource access, time/data/CPU limits, cancellation and output limits.
Record model/policy version, input provenance, coverage, assumptions and freshness so
results are reproducible and gaps remain visible. A prediction is not a mutation.

Historical simulation needs retained orders/events and sufficient inventory snapshots
or reconstructable transitions. Define required inputs and retention before promising
coverage. Unsupported periods or rules produce an explicit incomplete/unsupported
result, never fabricated inventory. Simulation does not replay historical events into
live consumers. Operational replay remains the authorized, audited, idempotent recovery
path already specified above. Do not introduce a generalized simulation/rule engine.

### Repair plans, risk and execution

Prefer normal application/domain commands (request reconciliation, retry idempotent
processing) over direct SQL edits or manually marking work successful. Exceptional
administrative mutation requires separate explicit authorization and audit controls.
A plan captures source evidence and authority, reason, proposed/approved changes,
resource scope, preconditions/versions, preserved invariants, expected impact and a
verification method. Define source-of-truth policy per flow; a provider discrepancy
alone does not prove which quantity is correct.

Conceptual risk classes are read_only, safe_retry, bounded_mutation and
high_impact_mutation. Replay is safe_retry only if its specific idempotency and retained
deduplication guarantees hold. Provider inventory changes may be bounded mutations;
bulk order rerouting may be high impact. Authorization combines organization, role,
resource ownership, risk and approval policy at planning and execution. The illustrative
VIEWER/OPERATOR/ADMIN/OWNER mapping in product direction is not a finalized permission
matrix. High-impact work requires explicit scope-aware confirmation; changed scope or
stale preconditions invalidates approval and requires a new plan.

Use durable operation identity and owner idempotency keys where supported. Bound retries
and concurrency; distinguish an unknown provider outcome from a known failure. Fetch or
reconcile before repeating an uncertain non-idempotent write. Restart recovery must
not repeat completed effects. Expose partial completion, bounded compensation or manual
review when atomic cross-owner repair is impossible; never imply a distributed rollback.

Conceptual lifecycle: proposed → approved → executing → awaiting_verification → verified,
with failed outcomes recording the execution or verification stage. These are future
concepts, not a prescribed schema. Approval can be provided by explicit policy for
allowlisted low-risk work; it does not remove audit or authorization requirements.

Repair audit records must include actor (or system plus policy ID/version), organization,
resource, reason, proposed change, approved change, execution result, verification result,
timestamps and trace/correlation identifiers. Each owner preserves its records with
restricted access and defined retention; the timeline references them without replacing
audit evidence. Sanitization must preserve useful provenance without exposing secrets.

### Verification and policy-driven remediation

Command acceptance, a successful HTTP response or an emitted event is not verification.
Define expected postconditions and use an authoritative provider fetch, owning-service
read or reconciliation to test them, preserving reservations and concurrent updates.
Evidence includes observed values, source/version and observation time. Account for
provider propagation lag with bounded polling/backoff; stale reads, drift or exhausted
verification remain visible as awaiting verification or a classified failure.

The future Repair Framework cannot expose execution until its operation has a minimal
verification path. The later Repair Verification stage broadens recovery and operator
workflows. Failed verification reopens attention; it must not silently trigger a loop
of corrections. Both success and failure feed the Operational Timeline and Operations.

Self-healing follows explicit observe_only, suggest, require_approval or auto_repair
policy. Automatic repair needs an allowlist, thresholds, resource scope, rate/attempt
budgets, cooldowns, a disable mechanism, audit and verification. Recheck authorization
and conditions at execution; policy actor context is mandatory. High-impact repairs
cannot be launched directly by AI. Unknown failures default to observation/manual review.

### Historical state / Commerce Time Machine

Use append-only operational observations, owner audit/history records, versioned state
transitions, snapshots and reconstructable projections incrementally. Mutable current
state, sampled traces and expiring outbox rows are insufficient historical evidence.
Outbox delivery cleanup must not be mistaken for an event archive. Operational history
is not a claim that events are the domain's sole source of truth.

Each supported entity view (order, SKU/product, store, location, sync job, integration)
needs a documented coverage contract: available interval, baseline snapshot/version,
retained transitions, provider observation times, projection freshness and gaps.
Inventory quantities can be reconstructed only from a valid baseline plus all necessary
changes, with documented ordering/concurrency semantics. Without them show known facts
and unknown intervals, not an invented exact past state. Cross-service views do not
promise a globally consistent instant without an explicit consistency mechanism.

Data owners specify snapshot cadence, schema/version migration, retention/deletion,
rebuild boundaries and access rules before enabling historical simulation or the view.
Retention must coordinate replay deduplication, audit needs and privacy requirements;
deleted evidence limits reconstruction. Restores and projection rebuilds require tests.
Minimal snapshots for bounded simulation may precede the richer historical-state UI.

### Environment isolation and simulator controls

Environment (local/test/sandbox/staging/production), subscription plan and entitlements
are distinct. Sandbox policy selects synthetic data, constrained providers, limits,
retention, billing/delivery suppression and inexpensive deployment without weakening
implemented correctness. An optional Shopify development store must be explicitly
allowlisted. No separate Sandbox repository or business-logic fork is permitted.

Commerce Simulator / System Lab is an engineering control plane for synthetic scenarios,
not the side-effect-free simulation evaluator. Its controls need separate authorization,
credentials and target allowlists, bounded rate/duration, and fail-closed environment
checks. Production must reject failure injection and reset/reseed paths regardless of
plan/entitlement settings; a hidden UI toggle is insufficient isolation. Reset is scoped
to identifiable synthetic tenants and cannot cross into merchant data or credentials.
Future scenarios extend from duplicates/delay/consumer failure/DLQ/inventory race to
out-of-order webhooks, drift, provider timeout, partial sync, warehouse unavailability,
routing conflicts and repair/verification outcomes only as those workflows exist.

## Production engineering for each implemented scope

Omnira is a commercial product under active development with production-grade engineering
requirements from the first subsystem. Missing functionality is honest; deliberately
unsafe or disposable implementation is not. One PostgreSQL instance or one VM/Compose
can be appropriate. Quality does not require HA, Kubernetes, sharding, service mesh or
multi-region infrastructure without a demonstrated need.

- **Failure model:** identify relevant database unavailability/rollback, broker loss,
  duplicates/reordering, provider timeout/rate limits, invalid webhooks, expired
  credentials, partial sync, worker crashes/restarts, network loss, deployments during
  processing, stale cache and concurrent mutation. Test important failure behavior
  practically; document unhandled relevant concerns without pretending they are solved.
- **Bounded work:** explicit timeouts, context cancellation, connection limits, worker
  concurrency, queue/backpressure limits, retry budgets and backoff. Classify transient,
  permanent, invalid-input, authorization and rate-limit failures. Retry must not repeat
  business effects; avoid unbounded operations and blind retries.
- **Lifecycle:** graceful startup, dependency-aware readiness distinct from liveness,
  health reporting, bounded request draining, consumer shutdown, acknowledgement after
  commit and database/connection cleanup when each responsibility exists.
- **Database:** enforce owner-local foreign keys, tenant-qualified unique constraints,
  checks and indexes. Review query plans, transactions, locks/deadlocks, connection
  management, timeouts and backup strategy. Migrations are production artifacts: assess
  compatibility, large-table locks, deployment order and rollback/forward-fix. Do not
  casually rewrite migrations already applied outside local development.
- **API:** versioned predictable contracts, validation, resource authorization,
  pagination, request limits, timeouts, structured errors and idempotency where relevant.
  Preserve backward compatibility; do not leak stack traces, SQL errors, credentials
  or internal implementation details to clients.
- **Security:** assess authentication, tenant ownership, secrets, sensitive logging,
  CSRF/CORS, SSRF, webhook authenticity, provider tokens, dependency vulnerabilities and
  file handling as relevant to each feature. Security Hardening reviews the whole system;
  it never licenses knowingly insecure earlier work.
- **Observability:** useful structured logs, metrics, trace spans, correlation and error
  classes accompany important workflows. Bound cardinality, volume and retention;
  sensitive data stays protected. Signals must help diagnose business behavior.
- **Deployment:** document startup, health checks, secret injection, bounded logs and
  rollback/forward recovery for the selected scale. Exercise backup/restore before
  relying on durability; low-cost hosting does not exempt operational safety.
- **Temporary code:** document its narrow scope and replacement trigger, show why it is
  safer/cheaper than premature abstraction, and preserve correctness/security. Sandbox
  never receives second-quality domain behavior.

Production-quality implementation for the current scope is different from unrestricted
Production readiness. Before real merchant launch, record evidence for security, data
integrity, backup/restore, migrations, observability, incident response, provider failure
behavior, rate limits, load characteristics, deployment/rollback, credential protection,
privacy and compliance requirements and support procedures. Phase 24 plans and gates this
review; a design document or a completed foundation phase cannot substitute for it.
