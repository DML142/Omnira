# Security and operational baseline

Tenant isolation and credential handling are release invariants. Organization context
must be authenticated and enforced in every owner service, not inferred from a UUID
or trusted merely because Gateway routed the request. Tenant-qualified constraints,
queries, APIs and integration tests cover orders, products, inventory, stores,
integrations, operational events and audit entries.

Identity uses Argon2id, short-lived access tokens and rotated refresh sessions.
Cookie-authenticated requests require appropriate CSRF protection, Secure/HttpOnly
cookies and explicit SameSite behavior. Input validation, RBAC, rate limits and safe
machine-readable errors accompany each endpoint. Log neither tokens nor credentials.
Integrations verifies raw webhook signatures, validates installation state, encrypts
credentials at rest and restricts raw payload access. Runtime database roles have
access only to the owning service schema.

Before any public sandbox: verify TLS, private internal endpoints, tenant/RBAC tests,
rate/usage limits, synthetic-only demo data, disabled external delivery/billing,
secret scanning, dependency review, backup/restore, rollback and explicit retention.
The later security phase deepens these controls; it does not postpone them.

Each data owner defines retention and deletion for its raw deliveries, audit entries
and operational events before storing public-deployment data. Platform operations
owns telemetry retention and access. Define measurable backup recovery objectives and
exercise restores before making durability claims. Commercial retention, support and
availability commitments require evidence and an explicit readiness review.

If a credential enters history, revoke/rotate it immediately, assess exposure, and
coordinate history cleanup. Removing the latest file is insufficient. No current
workflow provisions services, deploys infrastructure or establishes a compliance
certification. Hosting branch protection and external scanners must be configured
when a remote repository is established.
