# Intended system boundaries

The diagram describes the target business flow. Phase 00 provides the minimal web
application, Gateway liveness and local PostgreSQL/RabbitMQ/Redis infrastructure.
The web page makes no API calls yet; business services and the arrows below remain
planned.

```mermaid
flowchart LR
  Web[Next.js application] --> Gateway[Go / Gin Gateway]
  Gateway --> Identity[Identity]
  Gateway --> Orders[Orders]
  Gateway --> Inventory[Catalog / Inventory]
  Gateway --> Integrations[Integrations]
  Provider[Mock / Shopify] -->|validated webhook ingress| Gateway
  Integrations -->|normalized event via outbox| MQ[RabbitMQ]
  Orders -->|outbox| MQ
  Inventory -->|outbox| MQ
  MQ --> Orders
  MQ --> Inventory
  MQ --> Notifications[NestJS Notifications]
```

Each stateful service has owner-restricted PostgreSQL storage. Redis is temporary
infrastructure. Standard public API traffic enters through Gateway; internal endpoints
remain private. See [system architecture](../architecture/system.md).
