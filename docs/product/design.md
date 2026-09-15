# Design source of truth

Status: design requirements, not implemented screens. English is the source locale.

## Frontend stack

Use:

```text
Next.js
TypeScript
App Router
React
Tailwind CSS
shadcn/ui where appropriate
TanStack Query
Zustand
React Hook Form
Zod
```

Use server/client boundaries intentionally.

Do not blindly make every component a client component.

## Frontend identity

Omnira has its own visual identity.

The visual direction is:

> dark-first operational interface with near-black surfaces, graphite elevation, restrained scarlet/red accents, high information density, and premium developer-console quality.

The inspiration may include the polished feel of products such as Render, Linear, and infrastructure dashboards.

Do not clone Render visually.

Do not use Render's purple palette.

Do not clone Shopify branding.

Omnira must remain visually distinct.

## Canonical theme

The canonical default theme is:

```text
Omnira Scarlet
```

General characteristics:

```text
near-black background
dark graphite surfaces
subtle lighter raised surfaces
almost-white primary text
muted neutral secondary text
scarlet/crimson primary accent
controlled red hover states
subtle red selected states
neutral borders
green success
amber warning
red critical
blue informational
```

Use red sparingly.

The interface should remain mostly neutral dark UI with scarlet identity accents.

Do not make every surface red.

## Design principles

The application interface must be:

```text
dark-first
dense but readable
operational
serious
high-information
minimal visual noise
functional before decorative
accessible
themeable by design
```

Avoid generic dashboard aesthetics.

Forbidden default visual patterns:

```text
heavy gradients
glassmorphism
huge rounded cards
oversized metric tiles
excessive shadows
decorative charts
random icons
large empty areas
startup landing-page styling inside the app
unnecessary animation
```

## Semantic design tokens

Do not hardcode presentation colors throughout components.

Use semantic design tokens.

Examples:

```text
--background
--surface
--surface-raised

--foreground
--foreground-muted

--accent
--accent-hover
--accent-muted
--accent-foreground

--border
--border-strong

--success
--warning
--critical
--info
```

Tailwind utility usage should prefer semantic tokens such as:

```text
bg-background
bg-surface
text-foreground
text-muted
border-border
bg-accent
```

Avoid hardcoding:

```text
bg-zinc-950
text-gray-400
bg-red-600
border-neutral-800
```

inside ordinary application components.

## Theme personalization architecture

The UI must be designed from the beginning so that a full appearance system can be added without rewriting components.

The feature does not block MVP delivery, but the token architecture must support it.

Future appearance settings may include:

```text
preset
base theme
accent color
contrast
density
radius
sidebar mode
motion preference
```

Initial canonical preset:

```text
Omnira Scarlet
```

Possible future presets:

```text
Omnira Scarlet
Obsidian
Ember
Graphite
Arctic
Forest
Ocean
Custom
```

Do not implement dozens of presets.

## Theme persistence

Initial appearance settings may use:

```text
localStorage
```

A future authenticated experience may sync preferences through the user profile API.

Theme settings should eventually support:

```text
export
import
versioned schema
validation
migration
reset to defaults
```

Example concept:

```json
{
  "schema": "omnira-theme",
  "version": 1,
  "name": "My Scarlet",
  "appearance": {
    "base": "dark",
    "accent": "#dc2626",
    "density": "compact",
    "radius": "medium"
  }
}
```

Imported themes must be validated.

Unsafe or unreadable configurations must be prevented or automatically corrected.

## Accessibility

Accessibility is mandatory.

Design must account for:

- contrast
- keyboard navigation
- focus visibility
- screen reader semantics
- reduced motion
- readable status indicators
- non-color-only state communication

Do not make error/success/status information understandable only from color.

## Density

Support future interface density modes:

```text
comfortable
compact
```

Compact mode is especially relevant for:

- orders tables
- inventory tables
- operations lists
- high-volume users

The component system should not assume only large comfortable spacing.

## Application layout

Standalone application layout should approximately support:

```text
sidebar
top context/header
organization/store selector
main content area
page-level actions
filters
tables
detail views
operational timelines
```

Likely navigation:

```text
Dashboard
Orders
Inventory
Products
Operations
Integrations
Automations
Settings
```

Automations may not exist initially.

Only expose capabilities supported by real data and behavior. Do not add empty
AI Diagnosis, Time Machine, Self Healing or Repair Center pages; future concepts
belong in planning until a useful supported workflow exists.

## Tables are first-class UI

This is an operational SaaS.

Tables are more important than decorative cards.

Orders example:

```text
Order
Channel
Customer
Status
Inventory
Total
Created
```

Inventory example:

```text
SKU
Product
Location
Physical
Reserved
Available
Allocated
Status
```

Integrations example:

```text
Store
Provider
Last Sync
Webhook Status
Errors
State
```

Tables should eventually support where relevant:

- pagination
- sorting
- filters
- column visibility
- bulk actions
- loading states
- empty states
- failure states

## Dashboard philosophy

The dashboard should answer:

> What requires attention right now?

Example useful metrics:

```text
Orders today
Awaiting fulfillment
Inventory alerts
Failed syncs
```

Then:

```text
Requires attention
Recent operational activity
Important failures
```

Avoid dashboards filled with meaningless graphs.

## Operational Timeline

Operational Timeline is a signature Omnira feature.

Order example:

```text
14:20:01 Order received from Shopify
14:20:01 Order normalized
14:20:02 Inventory reservation requested
14:20:02 2× SKU-293 reserved in Warsaw
14:20:03 Order confirmed
14:20:04 Notification delivered
```

Failure example:

```text
14:20:02 Inventory reservation failed
          Warsaw Warehouse
          Insufficient available inventory
```

The timeline should connect technical distributed-system behavior to a business-readable interface.

## Progressive developer details

Normal users should not need to see:

```text
correlation_id
causation_id
routing key
exchange
trace span
```

These should appear behind a developer/details view.

Example:

```text
Developer details
- Event ID
- Trace ID
- Correlation ID
- Producer
- Retry count
- Raw payload
```

Keep the main UX business-readable.

## Embedded Shopify experience

Omnira may eventually run embedded inside Shopify Admin.

The embedded experience should follow Shopify-compatible interaction patterns where appropriate.

Use Shopify integration tools where required.

However:

```text
Shopify-compatible interaction
+
Omnira-native visual identity
```

is preferred over visually cloning Shopify.

The canonical Omnira dark/scarlet identity remains the product identity.

## Marketing site

Marketing UI and application UI are separate concerns.

The marketing site may have stronger visual storytelling and branding.

Application UI must remain operational and restrained.

Do not carry landing-page styling into core application screens.

## Localization / i18n

Omnira must be localization-ready from the beginning.

This is an architectural requirement even if the first implementation ships in one language.

Rules:

- Do not hardcode user-facing text throughout components.
- Use a centralized translation/i18n system.
- UI strings must be represented by translation keys.
- Date, time, number, currency, pluralization, and locale-sensitive formatting must use locale-aware APIs.
- Never manually format currencies or dates using language-specific assumptions.
- Language should be selectable from Settings.
- Future server-side persisted language preference should be possible.
- Initial language preference may fall back to browser locale.
- English should be the primary source locale.
- Additional translations can be added later without component rewrites.
- Error codes from backend should remain machine-readable and be translated on the frontend where appropriate.
- Backend domain logic must never depend on translated strings.
- User-generated content must never be passed through translation keys.

Do not spend early roadmap phases translating the entire product.

The requirement is to make the frontend i18n-ready so localization becomes incremental later.

## Frontend structure

Suggested structure:

```text
apps/web/
├── app/
│   ├── (auth)/
│   ├── (dashboard)/
│   │   ├── dashboard/
│   │   ├── orders/
│   │   ├── inventory/
│   │   ├── products/
│   │   ├── operations/
│   │   ├── integrations/
│   │   └── settings/
│   └── api/
│
├── components/
│   ├── ui/
│   ├── layout/
│   ├── orders/
│   ├── inventory/
│   ├── integrations/
│   └── operations/
│
├── features/
│
├── lib/
│   ├── api/
│   ├── query/
│   ├── auth/
│   ├── validation/
│   └── i18n/
│
└── styles/
```

Do not create a separate embedded Shopify application immediately.

If embedded and standalone experiences diverge significantly in the future, restructuring can be considered through an ADR.

## Initial token specification

Values below define the initial dark preset. Verify contrast in rendered components
before shipping; custom accents must not replace semantic status colors.

| Token | Initial value |
| --- | --- |
| --background | #0c0d10 |
| --surface | #15171b |
| --surface-raised | #202329 |
| --foreground | #f5f5f6 |
| --foreground-muted | #a8abb3 |
| --accent | #b91c1c |
| --accent-hover | #991b1b |
| --accent-muted | #351719 |
| --accent-foreground | #ffffff |
| --border | #343840 |
| --border-strong | #606672 |
| --success | #4ade80 |
| --warning | #fbbf24 |
| --critical | #f87171 |
| --info | #60a5fa |

Use a system sans-serif stack and tabular numerals for quantitative columns. Default
body text 14px, minimum supporting text 12px; 4px spacing grid and restrained 6px
control radius. Start with compact table rows around 36px and comfortable rows around
44px; interactive targets and keyboard access must remain usable in either density.
Use visible focus rings with offset, not accent text alone. Target WCAG AA: 4.5:1
normal text, 3:1 large text and meaningful UI boundaries. Measure actual pairings.

## Interaction contracts

Forms have persistent labels, field-level errors, an error summary where useful,
explicit required fields, and preserved input on failure. Buttons distinguish
primary, secondary, and destructive intent with labels. Destructive/replay actions
show affected scope and require confirmation when their business impact warrants it.
Dialogs have accessible names, focus trapping, Escape where safe, and focus return.
Alerts explain consequence and a recovery action; never expose raw backend errors.

Loading tables retain structure and announce busy state. Empty states distinguish
no data from no filter matches and permission denial. Failures offer retry without
silently showing stale data as fresh. Sorting and pagination operate on the server
for unbounded datasets; selections must not silently cross organization changes.

On smaller screens collapse navigation, preserve page actions, and permit labeled
horizontal table scrolling rather than hiding critical order/status information.
Do not shrink type to fit. Timeline entries include time, action, outcome, and relevant
location; technical identifiers are opt-in details with sensitive payload redaction.
Motion stays short and purposeful; respect prefers-reduced-motion without animation.

## Delivery order

Phase 12 starts semantic tokens and translation-key plumbing before any business UI.
Phase 16 adds validated appearance persistence/customization; Phase 17 adds language
selection and locale coverage. Neither phase permits earlier hardcoded colors or UI
strings. Zustand is for local UI state; TanStack Query owns server state; forms use
React Hook Form and Zod when those responsibilities first exist. Default to server
components and isolate interactive client boundaries. Do not install the entire
frontend dependency list merely to produce an empty shell.

## Future operational loop patterns

These patterns extend Omnira Scarlet; they do not authorize screens in Phase 00.
Preserve dark-first near-black surfaces, graphite hierarchy, restrained scarlet,
semantic statuses, personalization, dense readable UI and progressive disclosure.
Each pattern enters the UI only after its underlying capability is real.

### Timeline and Operations workspace

Operational Timeline is the primary entry point to chronology, cause, related entities,
failure explanation, restricted developer details, supported repairs and verification.
Start with concise time/action/outcome entries. Later a failed reservation may show its
reason, causal order, affected SKU and a supported next action. Offer Explain, causal
graph and Simulate repair only when their backing behavior exists.

Operations eventually unifies incidents, failed integrations/syncs, DLQ items, drift,
blocked orders, suggestions, recent repairs and verification failures. Prefer actionable
lists with scope, age, severity, owner and next step. Make incomplete data, projection
lag and missing permissions visible; avoid misleading all-clear status. Link back to
entity timelines instead of duplicating disconnected diagnostic screens.

### Causal graph and explanation panel

Use a bounded directed operation graph with clear reading order, grouping,
expand/collapse, resource labels, status, timestamps and concise explanations. Provide
keyboard navigation and a linear accessible equivalent. Avoid animated force-directed
spaghetti graphs. Show missing parents/evidence as gaps, never invented connecting
causes. A graph should answer why this operation reached this state.

Explanation panels separate recorded facts, deterministic derivations and optional
labeled AI-assisted interpretation, with evidence references and observation freshness.
Lead with merchant language: “Reservation failed because Warsaw has insufficient
available stock.” Show supported alternatives and actual constraints separately.
Advanced details may expose event_id, trace_id, correlation_id, causation_id, producer,
routing key, attempt count and redacted payload/resource references only with appropriate
access. Infrastructure jargon and raw payloads are not the default experience.

### Simulation results

Clearly label CURRENT STATE, PROPOSED CHANGE, PREDICTED RESULT, RISKS and AFFECTED
RESOURCES. Include input period, coverage, model/policy version, assumptions, freshness
and unknowns. Compare only meaningful supported metrics. Use a persistent “Simulation —
no changes applied” label and textual status, never a success banner implying execution.
Moving from prediction to execution requires a separate supported repair flow and
fresh validation; stale results cannot authorize mutations.

### Repair plan and risk confirmation

Follow detected issue → explanation → suggested repair → preview impact → authorization
and confirmation → execution → verification. Plans show before/after values, preserved
reservations/invariants, affected resources/orders, source-of-truth evidence and expected
verification. Make authorization failures and stale plans understandable.

Conceptual risk labels are read_only, safe_retry, bounded_mutation and
high_impact_mutation, translated into plain language. High-risk confirmation must show
the exact action, tenant/store scope, quantities, impact and recovery limitations; a
generic “Are you sure?” dialog is inadequate. Changed scope or evidence requires renewed
review. Disable repeated submissions while work is in progress, without hiding recovery
or the durable operation reference.

### Verification and historical state

Show proposed, approved, executing, awaiting_verification, verified and failed as
conceptual future states, using text/icons as well as color. Distinguish command accepted,
execution completed and outcome verified. Display verification source, observation time,
expected/observed values and failure stage. Awaiting verification never looks complete;
failed verification returns the issue to operator attention.

The historical state viewer offers entity/time context, known quantities and nearby
transitions with provenance, freshness and retention/coverage gaps. Distinguish recorded
snapshots, reconstructed values and unknowns. Never imply an exact historical state
where data is incomplete or globally synchronized when it is not. Historical inspection
must remain visibly separate from live state and mutation controls.

### Environment and localization

Use Omnira Sandbox externally and Sandbox or Demo Sandbox for the environment badge.
Show plan separately. Authorized Sandbox System Lab failure/reset controls require
explicit synthetic scope; Production must reject these paths at the backend.

Every explanation, simulation, repair, verification, incident and risk string uses
existing translation keys, locale-aware quantities/times and pluralization. Backend
reason codes plus structured metadata select localized wording; business logic never
matches translated text or arbitrary English logs. Preserve non-color-only semantics,
focus handling, reduced motion and theme contrast in every new pattern.
