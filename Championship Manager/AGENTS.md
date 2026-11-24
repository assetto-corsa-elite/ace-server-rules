# Championship Manager feed

**Required for VSC/CM implementation:** read [VSC_INTEGRATION.md](VSC_INTEGRATION.md) first and follow its required reading order. Build native CM actions and Discord actions on the same backend. Preserve the producer/integrator boundary.

Read README.md, PRODUCTION.md CONSUMER.md and ANNOUNCEMENTS.md before preparing or updating a sequence.

- Author the actual English posts and PNG assets here. CM consumes them through catalog.json.
- Retain stable sequence/post IDs across revisions. Update SHA-256 values and revision together.
- Use driver and checked-emoji tokens. The stable identity registry is authoritative.
- Include team performance and team poster sections when pertinent, especially forecasts.
- Validate every imported snapshot with tools/feed.py and run the regression tests after code changes.
- Visually inspect posters and keep structured, short text. Never claim Discord rendering was tested without checking an actual destination preview.
- Existing archived sequences are historical. New ready sequences require a confirmed publication time, assets and completed post-race review where applicable.
- Keep changes scoped to this directory and the repository's navigation link. The CSP video and server settings have separate instructions.

Preserve editorial detail. The user identified indentation and dense paragraphs as the issue, not overall volume. Follow the audit status in AUDIT.md and never describe documented cadence as an active generation or delivery service.

Read EDITORIAL.md for every new production. Give stages distinct editorial purposes, maintain a fact-based round storyline, cover relevant teams and midfield progress, and use fresh caustic humour. Preserve information through structure rather than shortening the package by default.

See [CAROUSELS.md](CAROUSELS.md) for native embed poster viewers, persistent Previous/Next navigation and the categories whose posters remain directly visible.

## Stewarding Review

Apply [STEWARDING.md](STEWARDING.md): add a text-only review after Race Results, include its condensed decisions in the announcement, and gate all post-race release on organizer-supplied decisions plus verified ACSM numeric adjustments and refreshed publication data. Preserve the durable decision history.

## Automated steward workflow

[STEWARDING_WORKFLOW.md](STEWARDING_WORKFLOW.md) specifies Sunday 15:00 CET report cutoff, Sunday 23:00 CET finalization, the role-authorized permanent panel, ENTRANTS-backed sanction wizard, automatic verified ACSM application and organizer-tagged results-ready notification. This deadline replaces the prior Sunday 20:00 rule for future live results.

## Authoritative owner decisions

[OWNER_DECISIONS.md](OWNER_DECISIONS.md) supersedes earlier recommendations on review finalization, publication control, cancellation, MEE6 report scope, manual bans and the one-hour owner-response timeout. Apply those decisions before implementing this workflow.
