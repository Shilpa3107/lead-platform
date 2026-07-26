# Migration Plan — OrderFlow order-processing route

## Principle
Every phase below ships independently and leaves the system in a working,
deployable state. Nothing here requires downtime, and nothing requires all
phases to land before value is delivered — phases 1-2 alone remove the two
most dangerous issues within the first week.

## Week 1 — Contain the critical risk, no behavior change
- Move all secrets (Stripe key, SendGrid token, DB credentials) to
  environment variables. Rotate the exposed keys with the provider first —
  a hardcoded secret that's already been committed must be treated as
  already compromised, even if the repo is private.
- Replace all string-interpolated SQL with parameterized queries
  (`cur.execute("... WHERE id = %s", (product_id,))`), closing the
  injection hole without touching any other logic.
- Add basic Pydantic-style request validation so malformed input produces
  a clean 4xx instead of an unhandled crash.
- **Why week 1 specifically:** these are drop-in fixes that don't require
  restructuring anything else. They can ship same-day once secrets are
  rotated, with no risk of breaking the working parts of the endpoint.

## Month 1 — Close the correctness gaps
- Wrap the stock-check, decrement, and order-insert in a single database
  transaction with row-level locking, closing the overselling race.
- Add an idempotency key to the Stripe charge call, closing the
  double-charge risk on retry.
- Add integration tests covering: successful order, insufficient stock,
  payment failure, and a simulated concurrent-order race — so these fixes
  are provably correct and protected against regression going forward.
- **Why month 1 and not week 1:** these require more careful, tested
  changes than a find-and-replace — a rushed transaction/locking change
  is itself a risk if untested, so it gets the time it needs rather than
  being forced into the fastest possible window.

## Quarter 1 — Structural refactor
- Split the single route handler into layers: pure pricing logic (no I/O,
  fully unit-testable), an order service (owns the transaction and
  coordinates payment/persistence/notification), and a thin route handler
  that just wires request → service → response.
- Extract payment and notification calls behind small interfaces
  (`charge_card()`, `send_order_confirmation()`) so they can be mocked in
  tests and swapped later without touching business logic.
- Backfill full unit test coverage for the pricing module and service
  layer, now that they're isolated enough to test in milliseconds without
  hitting a real database or Stripe.
- **Why this is last, not first:** this phase is valuable but not urgent
  — none of it closes a live security or correctness risk on its own. It's
  the deferred cost of the original quick-and-dirty approach, and it's
  safe to schedule after the actual fires (weeks 1 and month 1) are out,
  rather than competing with them for priority.