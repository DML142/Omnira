# ADR-003: Use RabbitMQ for operational events

Status: accepted

## Decision

Use a topic exchange, durable per-consumer queues and at-least-once delivery. Do not introduce Kafka.

## Reason

Operational workflows need routing, acknowledgement and bounded recovery.

## Tradeoff and consequence

Duplicates and reordering must be handled by domain consumers; broker operations remain a deployment responsibility.
