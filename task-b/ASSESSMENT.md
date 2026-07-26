# Codebase Assessment — OrderFlow order-processing route

## Summary
The `/orders` endpoint works, but concentrates business logic, external I/O,
and persistence in a single function with no test coverage, and contains
several issues serious enough to require immediate action rather than
gradual cleanup.

## Issues, ranked by risk

### Critical — fix immediately, before any other work

**1. Hardcoded secrets in source (Stripe live key, SendGrid token, DB password)**
- Risk: anyone with repo read access — including in git history, even after
  deletion — can charge live cards, send arbitrary email as this business,
  or connect directly to production data.
- This is the one issue where "leaving it in place one more sprint" is not
  an acceptable tradeoff; a leaked live payment key is an active, ongoing
  financial liability every hour it's exposed.

**2. SQL injection via string-interpolated queries**
- Risk: `data["product_id"]` and `data["email"]` go directly into SQL
  strings. Any user who understands the request shape can read or modify
  arbitrary rows, not just their own order.
- Distinguishing this from issue #1: this requires an attacker to actually
  probe the endpoint, whereas the secrets are exploitable by anyone who
  simply *reads* the repo. Both are critical, but the secrets issue has a
  lower bar to exploitation.

### High — fix before the next significant feature is added on top

**3. No transaction around stock check + decrement + order insert**
- Risk: concurrent requests for the same product can both pass the stock
  check before either commits, allowing overselling. A failure between the
  Stripe charge and the DB commit can charge a customer with no order
  record — a support and trust problem, not just a data-integrity one.

**4. No idempotency on payment charges**
- Risk: a timeout or retry (client-side or infrastructure-level) can charge
  the same card twice for one order, since nothing tells Stripe "this is
  the same request as before."

### Medium — real problems, but bounded and non-urgent

**5. All logic in one function — no separation of pricing, payment,
   persistence, and notification**
- Risk: this isn't a security or correctness bug today, but it's why the
  above bugs are hard to find and will stay hard to test even after
  they're patched individually. It's the root cause that makes future
  regressions likely.

**6. No input validation — raw dict access, unhandled KeyErrors**
- Risk: malformed requests crash with a raw 500 instead of a clean 4xx,
  which is a poor API contract but not a security hole on its own.

## Why this ranking, not severity-by-gut-feel
Critical issues are ones that are exploitable *right now*, by a low-effort
attacker, with material financial or data consequences. High issues are
correctness bugs that will definitely bite eventually under real traffic,
but require specific timing/concurrency to trigger. Medium issues are
structural debt that makes everything else harder to fix safely, but
aren't themselves a live incident waiting to happen.