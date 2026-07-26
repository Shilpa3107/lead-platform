# Engineering Standards Proposal

## Standards to introduce
1. **No secrets in source, ever** — enforced by GitHub push protection /
   secret scanning at the repo level (not just a written rule), so it's
   caught mechanically, not by memory or code review discipline alone.
2. **All SQL through an ORM or parameterized queries** — no raw string
   interpolation into queries, enforced by linting (a grep-based CI check
   for `% (` patterns near `execute()` calls is a cheap first pass even
   before a full ORM migration).
3. **Business logic separated from route handlers** — a route handler's
   job is request→response wiring; anything else (pricing, external calls,
   persistence coordination) belongs in a service layer.
4. **New code ships with tests for its core logic** — not 100% coverage as
   a mandate, but no new business-logic function merges without at least
   one test exercising it.

## Getting a resistant team to actually adopt this
The realistic failure mode for standards proposals isn't disagreement —
it's that everyone nods in the meeting and nothing changes because the old
patterns are faster in the moment and no one enforces the new ones under
deadline pressure. So the plan leans on mechanism over persuasion:

- **Lead with the cheapest, least controversial win first**: turn on
  GitHub's secret scanning immediately — it's a checkbox, not a debate,
  and it already caught a real issue in this exact project during Task B
  drafting (an example secret placeholder briefly tripped push
  protection), which is a concrete, recent story to point to internally
  rather than an abstract argument for why this matters.
- **Make the standard mechanical, not aspirational**: a CI lint check that
  fails a PR is far stickier than a wiki page nobody reads. Standards that
  rely on every reviewer remembering to check for something by hand decay
  within a few sprints; standards enforced by tooling don't.
- **Apply new standards to new code only, not as a retroactive mandate**:
  asking a team to fix all existing violations before shipping anything
  new guarantees resistance, since it's pure overhead with no visible
  feature progress. Enforcing standards only on the diff being merged
  keeps the cost proportional and the pushback low.
- **Show the refactor, don't just describe it**: a concrete before/after
  example (like the one in this task) that demonstrates the new pattern
  is more convincing to a skeptical engineer than a style guide, because
  it's checkable against real tradeoffs rather than taken on faith.