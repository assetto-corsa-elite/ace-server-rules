# Championship Manager feed

Read README.md, PRODUCTION.md CONSUMER.md and ANNOUNCEMENTS.md before preparing or updating a sequence.

- Author the actual English posts and PNG assets here. CM consumes them through catalog.json.
- Retain stable sequence/post IDs across revisions. Update SHA-256 values and revision together.
- Use driver and checked-emoji tokens. The stable identity registry is authoritative.
- Include team performance and team poster sections when pertinent, especially forecasts.
- Validate every imported snapshot with tools/feed.py and run the regression tests after code changes.
- Visually inspect posters and keep structured, short text. Never claim Discord rendering was tested without checking an actual destination preview.
- Existing archived sequences are historical. New ready sequences require a confirmed publication time, assets and completed post-race review where applicable.
- Keep changes scoped to this directory and the repository's navigation link. The CSP video and server settings have separate instructions.
