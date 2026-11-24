# Championship Manager

ACE publication feed for Championship Manager. ChatGPT/Codex authors the posts and posters here. CM reads the feed, shows the available sequences in its UI and delivers their messages to Discord in order.

## Entry point

| Item | Repository path |
| --- | --- |
| Machine catalog | `Championship Manager/catalog.json` |
| Publication cadence | `Championship Manager/config/publication.json` |
| Stable driver identities | `Championship Manager/config/identities.json` |
| Checked custom emoji | `Championship Manager/config/emojis.json` |
| Sequence contract | `Championship Manager/schemas/sequence.schema.json` |
| Consumer integration contract | [CONSUMER.md](CONSUMER.md) |
| Editorial and visual requirements | [PRODUCTION.md](PRODUCTION.md) |
| Reference validator and renderer | [tools/feed.py](tools/feed.py) |

Repository: `assetto-corsa-elite/ace-server-rules`, branch `main`.
Read `catalog.json` at a resolved commit SHA. Fetch every manifest, text and attachment from that same SHA. Paths inside manifests are relative to this directory.

## Publication sequence

1. Practice Highlights and Forecast, Friday at 19:00 CET.
2. Pre-Race Briefing, at the explicit time set for that round.
3. Qualifying Report, Race Results, Race Insights, Driver/Team Standings and Next-Round Forecast, Sunday at 20:00 CET, after race review.

Each sequence carries an explicit timezone-aware `scheduled_at`. The Friday/Sunday settings guide production; they do not create missing content. Pre-race briefing time is still unset because ACE has not supplied a recurring time for it.

## Available content

Four historical Nordschleife Round 4 sequences are included: the pre-race briefing, the post-race package and the two announcement examples. They contain eight structured text templates and fourteen unique PNG posters, including the corrected Portimao forecast with its team section.

Their status is `archived` because they were already delivered for manual publication in this conversation. CM lists them in its archive view and excludes them from automatic delivery. Historical rendering now uses stable mention tokens and structured sections. Race figures, supplied review decision and posters remain grounded in the delivered source packages.

There are currently zero live `ready` sequences. New packages will be added by ChatGPT/Codex with their publication time and promoted to `ready` in one atomic repository commit.

## Local verification

Requires Python 3.10 or later. Run from the repository root.

```bash
python "Championship Manager/tools/feed.py" validate
python "Championship Manager/tools/feed.py" list
python "Championship Manager/tools/feed.py" plan --now 2026-11-29T20:00:00+01:00
python -m unittest discover -s "Championship Manager/tests" -v
```

The reference program validates hashes, UTF-8, templates, schedule metadata and order. `render` resolves tokens from a CM-produced binding file and prints a Discord content payload. It has no Discord sending code. CM integration, its UI, driver mapping and delivery worker are the next implementation step.

## Update protocol

ChatGPT/Codex adds source-grounded text and PNG assets, updates file SHA-256/byte sizes, then updates the manifest and catalog. The entire update lands in one commit. Stable sequence and post IDs survive revisions. CM keeps its delivery ledger in its own persistent database.

Code and configuration changes to CM itself belong in the later integration work. Discord tokens, credentials, guild/channel IDs and private driver database exports belong in CM's local configuration.

## Announcement routing

See [ANNOUNCEMENTS.md](ANNOUNCEMENTS.md) for race-day announcements at 09:00 CET, the three-message post-results announcement, channel ID configuration and the exact everyone policy. All other sequences use Results.

## Audit and implementation status

[AUDIT.md](AUDIT.md) distinguishes repository checks from pending producer scheduling, CM integration and real Discord acceptance tests. Text can be detailed; short sentences, line breaks and readable list structure are required.

## Editorial direction

[EDITORIAL.md](EDITORIAL.md) defines distinct roles for each post, a round-specific storyline, whole-field and team coverage, contextualized statistics and sharper, varied humour. Detailed content is retained through readable structure and successive messages.
