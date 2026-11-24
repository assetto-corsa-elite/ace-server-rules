# CM consumer contract v1

## Fetch and preview

1. Resolve `main` to a commit SHA. A git pull/checkout or GitHub API fetch is supported. Pin that SHA for the complete import.
2. Read `Championship Manager/catalog.json`, then the listed manifests at that SHA. Verify each manifest hash and all runtime configuration hashes. Use conditional requests or a sparse checkout so CM fetches this content directory without repeatedly downloading the repository's large video assets.
3. Validate the manifest schema, content SHA-256, PNG SHA-256, declared byte sizes and PNG signatures. Download the complete sequence before delivery. Check the destination guild's current attachment size limits.
4. Keep the previously validated snapshot available if an import fails. Mark the new snapshot as invalid in CM and retry fetching. Never combine files from two commits.
5. Display ready, draft, archived and cancelled sequences separately. Show track, round, scheduled local date/time, revision, ordered posts, text preview, ordered image thumbnails, validation errors and delivery status.

The catalog is a directory of content. Every message is a manifest post with `kind=text` or `kind=media`. Text posts contain a template and zero to ten ordered attachments. Media posts have null content. Direct posts upload at most ten attachments; carousel posts list every logical screen and upload only the active image. A message with four posters is one Discord message with four files. The next post follows only after successful completion of the previous post.

## Identity and emoji rendering

Template syntax is literal `{{driver:stable_key}}` and `{{emoji:checked}}`.

CM links each stable driver key to the existing driver database's Discord snowflake. Existing in-game aliases and known handles are hints for establishing that link. Resolve ambiguity explicitly and persist the chosen ID. The same key must resolve to the same ID throughout a sequence. Refresh data from CM's database before preparing the send batch, then freeze those bindings for that batch.

All checked emoji tokens use the same destination-guild emoji object with name `d_`. Resolve its actual ID and animation flag from CM's guild emoji lookup. Verify that the bot can use it. The configuration currently leaves the ID unset because a valid guild binding has not been verified.

Example binding file, using fabricated IDs only to illustrate the shape:

```json
{
  "drivers": {"lilcoughdrop": "123456789012345678"},
  "emojis": {"checked": {"id": "234567890123456789", "name": "d_", "animated": false}}
}
```

Render to `<@USER_ID>` and `<:d_:EMOJI_ID>` or `<a:d_:EMOJI_ID>`. Perform token substitution last. Preserve the resulting angle-bracket syntax byte-for-byte. A later Markdown conversion, underscore escaping, HTML encoding or shortcode conversion would corrupt it.

Use the reference `render` function with a validated snapshot. A missing driver or checked-emoji binding produces a clear CM mapping error for that message. CM can still show a template preview and its unresolved identities. Before a sequence starts, resolve all bindings and validate all rendered messages. Enforce the 2,000 UTF-16-unit content limit after substitution.

For ordinary posts, send `allowed_mentions` with `parse: []`, an explicit `users` list from the rendered tokens, `roles: []` and `replied_user: false`. A driver's display name may change on Discord; their snowflake and stable mapping remain the same.

## Scheduling and order

`status=ready` and a due `scheduled_at` make a sequence eligible. `draft`, `archived` and `cancelled` are excluded. Optional `expires_at` is an absolute cutoff. When CM returns after downtime, catch up eligible undelivered messages until that cutoff. With no cutoff, retain overdue messages in the queue.

Use ISO-8601 offsets as the scheduling authority. The production cadence is Friday 19:00 CET and verified-final-stewarding release by Sunday 23:00 CET for League 04 winter rounds. Dates/times in Discord text use Unix timestamps with `t` or `F`. PNG schedules must state their timezone.

A post-race sequence requires `race_review_complete=true` when made ready. This records the organizer's review completion. Pre-race briefing cadence remains unset; its producer must supply an explicit publication time when preparing a live sequence.

Within a sequence, send ascending contiguous `order` values. Optional `requires_sequences` names complete prerequisites. Process same-destination due sequences by publication time and sequence ID. At equal times, producer IDs must be chosen consistently with the intended sequence order, or encode that relation using `requires_sequences`. Dependencies are satisfied by CM's completed delivery records, not merely by their presence in GitHub.

## Delivery ledger and retries

Use CM's persistent database with a unique key consisting of `guild_id/channel_id/sequence_id/post_id`. Do not include revision or commit SHA in that unique key. Store source commit, revision, content/asset digest, destination, message ID, send state, attempt count and timestamps.

Suggested states are `pending`, `sending`, `sent`, `retryable_failure`, `needs_reconciliation` and `content_changed`. Acquire a database-backed destination lease and claim the next post transactionally so two CM workers cannot publish the same post concurrently.

Before creating a message, persist the attempt with a stable nonce derived from its delivery key. The reference helper returns a 24-character nonce. Use Discord's supported nonce deduplication when sending. After success, persist the returned message ID before advancing to the next post.

Discord nonce deduplication has a limited time window. A crash after Discord accepts a message but before CM records its ID is an ambiguous send. Reconcile with the destination using the stored nonce/message metadata when available. If a unique match cannot be established, show `needs_reconciliation` and resolve that attempt before proceeding. Blindly retrying an ambiguous send can create duplicates.

Respect Discord rate-limit responses and `retry_after`. Retry known pre-send/network fetch failures with bounded backoff and resume after restart. Persist progress after every acknowledged post. Later sequence posts wait until the failed post is resolved.

If an already-sent post changes in GitHub, show `content_changed` beside the stored message ID. A revision does not authorize creating a second message. The later UI can expose an explicit edit/republication action. Replaying an archive also requires an explicit CM UI action with a deliberate new delivery identity.

## First connection

CM imports the four historical sequences into its archive view. The current catalog contains zero ready sequences, so initial connection has nothing scheduled to send. Channel mapping, guild emoji binding and driver bindings are completed during CM integration. The repository contains publication data and a reference reader; Discord sending and scheduling will run in CM after that integration.

## Reference sources

- [Discord message resource, mentions and create-message fields](https://docs.discord.com/developers/resources/message)
- [Discord formatting reference](https://docs.discord.com/developers/reference#message-formatting)

## Announcement extension

[ANNOUNCEMENTS.md](ANNOUNCEMENTS.md) defines the two logical channels, runtime Results jump link, image-only message kinds and the authorized everyone exceptions. This extension governs notification permissions and announcement ordering. The reference renderer returns the correct allowlist for each kind.

## Poster presentation

Apply [CAROUSELS.md](CAROUSELS.md) at the post's existing sequence position. Read presentation.mode before building Discord files. Persist carousel views and use the reference screen renderer for embed/button payloads. Protect the direct individual/team posters and practice highlights.

## Stewarding Review

Apply [STEWARDING.md](STEWARDING.md): add a text-only review after Race Results, include its condensed decisions in the announcement, and gate all post-race release on organizer-supplied decisions plus verified ACSM numeric adjustments and refreshed publication data. Preserve the durable decision history.

## Automated steward workflow

[STEWARDING_WORKFLOW.md](STEWARDING_WORKFLOW.md) specifies Sunday 15:00 CET report cutoff, Sunday 23:00 CET finalization, the role-authorized permanent panel, ENTRANTS-backed sanction wizard, automatic verified ACSM application and organizer-tagged results-ready notification. This deadline replaces the prior Sunday 20:00 rule for future live results.

## Authoritative owner decisions

[OWNER_DECISIONS.md](OWNER_DECISIONS.md) supersedes earlier recommendations on review finalization, publication control, cancellation, MEE6 report scope, manual bans and the one-hour owner-response timeout. Apply those decisions before implementing this workflow.
