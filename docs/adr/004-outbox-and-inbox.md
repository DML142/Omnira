# ADR-004: Commit domain state with outbox and inbox

Status: accepted

## Decision

Write state and outbox in one transaction; consumers commit inbox, effects and outgoing events atomically before acknowledgement.

## Reason

Independent database and broker writes can lose or duplicate effects.

## Tradeoff and consequence

Workers, duplicate-safe consumers, publisher confirms and crash-window tests are mandatory. Exactly-once transport is not promised.
