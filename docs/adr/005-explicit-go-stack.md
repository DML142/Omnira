# ADR-005: Use Gin and explicit SQL in Go services

Status: accepted

## Decision

Use Gin HTTP, pgx, sqlc and goose. Compose dependencies explicitly and avoid GORM or a default DI framework.

## Reason

Transactions, locks, constraints and SQL must remain visible and testable.

## Tradeoff and consequence

More explicit query/mapping code is accepted in exchange for predictable ownership and concurrency.
