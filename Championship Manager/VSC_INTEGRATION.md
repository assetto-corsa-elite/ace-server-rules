# VSC implementation handoff: Post Results in Championship Manager

**Required reading before implementing or changing CM's league publishing integration.** This document is the implementation entry point. All user-facing CM labels and Discord copy must be in English.

## Read first

Read this file, then OWNER_DECISIONS.md, CONSUMER.md, ANNOUNCEMENTS.md, CAROUSELS.md, STEWARDING.md and STEWARDING_WORKFLOW.md in full. Read schemas/sequence.schema.json, schemas/stewarding.schema.json and config/*.json for the data contract. PRODUCTION.md and EDITORIAL.md govern authored content. README.md identifies the reference validation commands.

OWNER_DECISIONS.md governs permissions, manual bans, owner finalization and publication approval. This handoff adds the native CM interface and assigns integration responsibilities; it does not remove existing publication gates.

When working in a separate CM application repository, add this source URL and required-reading instruction to that repository's existing AGENTS.md or equivalent VSC project instructions. A file in this content repository is not automatically loaded by an editor working in another checkout. Preserve that application's existing instructions.

Canonical source: https://github.com/assetto-corsa-elite/ace-server-rules/tree/main/Championship%20Manager

## Responsibilities and boundaries

| Party/system | Owns | Must not assume |
| --- | --- | --- |
| ChatGPT/Codex content producer | Source-grounded analysis; English copy; posters and charts; identity tokens; ordered manifests, hashes and catalog updates; atomic content commits | Access to CM runtime, automatic generation outside an active session, or authority to invent steward decisions |
| VSC integration implementer | Inspect the existing CM application; connect this feed; build Post Results UI; persistent storage, workers, Discord interactions, ACSM adapter and deployment within that application's conventions | Editorial rewriting, invented results, invented API routes, duplicated entrant databases or report intake |
| CM runtime | Import/validate/cache; bind actual identities and channels; apply supplied numeric sanctions; track outstanding; show previews; enforce gates; schedule/send/resume; persist audit and delivery receipts | That a ready flag in GitHub alone grants publication or proves an ACSM update |
| Owner | Configure existing CM; finalize decisions, including zero penalties; review available package; approve/hold and control publication; manual bans | A new report-management process inside CM |
| League Stewards / Super Admins | Attribute already-decided sanctions; Super Admins may cancel sanctions | Owner-only review finalization or publication controls |
| MEE6 | Reports, evidence/intake and late-report handling | CM rebuilding or blocking on a new MEE6 report API |

This repository is the authored content feed, not the CM application source. VSC implements application code in the existing CM project. CM reads this repository; it does not require GitHub write permission. Never commit bot tokens, ACSM credentials, private channel configuration or private decision evidence here.

## Existing application inspection

Before coding, identify the existing left navigation framework, championship registry, ENTRANTS database and stable IDs, owner identity, authentication/role model, Discord client, persistence, background-job framework and actual ACSM editing mechanisms. Reuse these systems. Resolve concrete field mappings from application code rather than inventing names or endpoints.

Use existing championships as the authoritative tab source. Link each feed league_id to an existing championship ID explicitly. Never create a second championship/driver registry from the feed. Missing or ambiguous links are visible configuration issues.

## Navigation and championship scope

Add **Post Results** to CM's left sidebar. It must open a normal section of the existing application, not a Discord link or external placeholder.

Across its top, display one tab per existing championship using its current name. Update tabs when the championship registry changes. Use a scrollable accessible tab bar if needed. Preserve selection while navigating. An empty registry shows `No championships available`.

Within each championship, display these sub-tabs in this order:

| Sub-tab | Contents and main actions |
| --- | --- |
| Overview | Selected round; feed health; latest import; readiness blockers; deadlines; approval window; next publication; quick links to configuration and affected items |
| Sequences | Available packages and ordered message/poster previews; publication status and owner controls |
| Stewarding | Permanent-panel equivalent; attribute and cancel penalties; finalize round review |
| Penalty History | Searchable decision, cancellation, outstanding and manual-ban history |
| Publication History | Message-level delivery receipts, corrections, errors and owner-controlled recovery |
| Settings | Feed connection, championship mapping, Discord destinations and binding/permission status |

All queries and mutations must carry the selected championship and round explicitly. Changing a tab must not submit a draft or reuse another championship's selection. Mark a draft's original championship/round; require it to be reopened before submitting if context changed.

## Settings: fields the owner fills in

Reuse existing CM-wide fields and role bindings where available; show a link to them instead of requiring duplicate values. Keep inherited values visible. Per-championship settings are persisted in CM's private database.

| Field / English label | Requirement |
| --- | --- |
| Content repository | Default assetto-corsa-elite/ace-server-rules; read-only source |
| Branch | Default main |
| Content directory | Default Championship Manager |
| Championship mapping | Selected existing CM championship linked to feed league_id; required |
| Discord server | Existing guild selector or Guild ID field; required |
| Results channel ID | Default for ordinary sequences; required for those deliveries |
| Announcements channel ID | Race-day and three-message results announcement destination |
| Stewarding panel channel ID | Permanent Discord panel destination; optional if using CM-only stewarding |
| Sanction summaries channel ID | Destination for the existing per-case summary messages |
| Results-ready alerts channel ID | Required owner-tagged ready notification destination before its approval timer starts |
| Owner Discord user ID | Reuse the configured organizer identity; required for owner actions and ready alert |
| League Stewards / Super Admins roles | Reuse actual guild role-ID bindings; never infer from display names |
| Sequence / message destination overrides | Select a known sequence, category or post ID and enter Channel ID; show inherited destination alongside override |
| Import refresh interval | Persist a bounded non-zero interval, default 300 seconds; manual Refresh now remains available |
| Automatic publishing | Owner-controlled switch, off on first connection; show missing prerequisites before enabling |

Provide Save settings, Test connection, Validate channels and Refresh now actions, with per-field errors and last successful check. Test operations must not send production posts or apply sanctions. A separate explicitly selected preview/test action may target a configured test channel and must show its destination first.

Verify channels exist in the selected guild, bot access, send/embed/attach permissions, emoji availability and applicable everyone permission. Validate action-specific permissions; do not ask for Administrator as a substitute. Preserve Discord IDs as strings.

Show resolved destinations for every message in a package. Freeze channel IDs and identity bindings once its delivery starts. Settings changes apply to unstarted deliveries; started deliveries require owner-controlled recovery to change destination.

A missing optional Discord steward panel must not disable the native Stewarding UI. A missing delivery/alert destination blocks only operations depending on that destination, with a named configuration error. Numeric sanctions accepted in CM must remain durable even if their Discord summary cannot yet be delivered; queue that summary separately and never repeat the numeric adjustment.

## Feed connection and readiness

Resolve main to one commit SHA. Fetch catalog, configuration, manifests, text and PNG assets at that same SHA. Download only the content subtree or requested files; avoid unrelated large video assets. Verify the complete snapshot using the existing contract and reference validator before accepting it. Retain the last valid snapshot when a new import fails.

Store last attempted/successful import, source commit, schema version and errors. Refresh now imports content, never publishes it. Respect API limits and conditional requests. Imported archived examples remain archived and cannot send on first connection.

Keep these states separate in the UI:

- Source state: draft, ready, archived or cancelled.
- Verification: valid, invalid, missing bindings, stale results or ACSM reconciliation required.
- Publication approval: awaiting owner, approved explicitly, approved by timeout or held.
- Delivery: scheduled, sending, partially sent, completed, failed or needs reconciliation.

Do not add unsupported states to the existing feed schema just to display runtime state. Store CM runtime states in CM's database.

If the post-race package is absent, show `Awaiting content producer`. If decisions/result fingerprints change, mark existing content stale and expose the required refreshed fingerprint/revision. VSC must provide a private integration seam or export of verified final data for the producer using the existing application architecture. Do not fabricate a live producer endpoint or promise autonomous AI regeneration as part of the feed reader. Publication stays blocked until a matching regenerated package is imported.

## Sequences and exact previews

Filter by round, phase, source status and delivery status. Each row shows championship, track, round, phase, sequence ID, revision, source commit, earliest release time with timezone, actual destination and blocker count.

Opening a sequence shows messages in manifest order. Each message displays:

- Category, order and stable post ID.
- Exact rendered English content, UTF-16 length and unresolved tokens/errors.
- Native mention targets and everyone notification policy.
- Direct poster thumbnails in attachment order, or a carousel with the exact screen labels and Previous/Next preview.
- Resolved destination and dependency status.
- For sent messages: Discord jump link, actual sent time and stored message ID.

Do not rewrite posts, summarize them, substitute invented pictures or change the order. Apply the canonical renderer and token bindings. Owner may request changes/hold from CM; content corrections normally return through a new producer commit. Avoid silent local edits that diverge from GitHub.

Owner controls: Approve now, Hold / request changes, Resume, Publish now, Retry failed delivery and Replay archived sequence. Only enable actions valid for the current state. Publish now changes timing only; it cannot bypass review, numeric verification, content freshness, dependency, permission or approval gates. Replay is explicit, shows a destination/notification preview and creates a deliberate new delivery identity. Ordinary retries keep the original identity.

Display the existing practice, forecast, full briefing, race-day announcement and post-race stages. Preserve Friday 19:00 CET, race-day 09:00 CET and Sunday 23:00 CET package-availability requirements. An unset full-briefing time is visible and requires an explicit time before its live release. Use the manifest offset as authority; do not silently reinterpret CET as summer time. Discord copy uses Unix timestamps.

## Native CM sanction workflow

Every stewarding action must be usable in CM without clicking a Discord panel or sending a Discord command. The optional permanent Discord panel and CM forms are two front ends to the same backend transactions and history.

Stewarding opens on the selected championship/round with a decision table showing driver, incident, reason, every sanction component, actor, timestamp, numeric application state and cancellation state. Show owner-only Finalize review and explicit No penalties controls with current blockers. A steward's Apply accepts a decision bundle; it does not finalize the whole round.

**Apply a penalty** opens this wizard:

1. Select driver from current championship ENTRANTS. Display in-game name, team and linked Discord identity. Handle refreshed entrants and retain historical identities.
2. Select incident type: Unsafe race start; Squeezing a driver; Divebombing; Blueflag infraction; Weaving (multiple defense moves); Brake checking; Unsafe pit exit.
3. Select sanction: 5 seconds; 20 seconds; 10 points deduction; 1, 2 or 3 outstanding penalties; Round ban; League ban; Servers and Discord ban.
4. Require Reason for outstanding and all bans. Require affected-round/scope for bans. Native CM uses a labelled text field equivalent to the Discord modal.
5. Show bundle preview with driver, round, incident(s), reasons and projected effects. Add another penalty returns to incident/sanction selection for the same driver/case. Allow combined seconds, points and outstanding.
6. Warn about previously treated matching cases. Require acknowledgement to continue a deliberate additional decision. Apply commits once, rechecks rights/revision and displays verified or pending/error state.

**Cancel a penalty** is Super Admin-only:

1. Select driver, including retained historical identities.
2. Select exact active decision/component with round/date, value, reason, case ID and status.
3. Enter required Reason for cancellation.
4. Preview reversal, outstanding effects and affected unpublished/published results.
5. Apply appends the cancellation, reverses applied numeric effects exactly once and verifies ACSM read-back. Keep the original event and cancelled label.

Native forms call the same service as Discord handlers. They must not simulate Discord clicks, duplicate application logic or require a Discord summary message ID as the decision's primary key. Show success in CM immediately after durable acceptance, then update verified application status asynchronously.

Outstanding threshold/reset, surplus, completed maximum history and manual ban handling follow OWNER_DECISIONS.md. Show active counter X/3, Max outstanding reached X/2, relevant history and manual enforcement status. Practice remains permitted under a round ban. No automatic ban adapter is required.

## Histories

Penalty History filters by championship, round, player, incident, sanction, actor, date and active/cancelled state. Show reasons, original/cancellation links, exact before/after changes, verified ACSM receipts, outstanding cycles and manual enforcement notes. Never delete audit events. Super Admin cancellation is accessible from a selected history row through the same required wizard.

Publication History filters by championship, round, sequence, destination and state. Show each attempted/sent message, source revision/commit, approval method, owner/timer events, timestamp, retry state, failure detail and Discord link when known. Owner can reconcile ambiguous deliveries and apply tracked corrections. Editing an already delivered message does not send another everyone ping.

Do not mix public publication assets with private stewarding reasons/evidence. Native history uses the existing private CM persistence and access controls, not a public GitHub dump of private data.

## Permissions in both interfaces

Check actual owner user ID and bound roles on every mutation, including final Apply after a draft. Reuse CM authentication and its existing trusted owner session. Do not invent another login system. A native session must map to its existing authorized actor; an unidentified actor cannot attribute sanctions.

| Action | Owner | League Stewards | Super Admins |
| --- | --- | --- | --- |
| Apply penalty | Only when existing steward/admin authorization also applies | Yes | Yes |
| Cancel penalty | Only when Super Admin authorization also applies | No | Yes |
| Finalize review; publication approve/hold/resume/replay | Yes | No | No |
| Configure destinations | Yes, through existing CM settings access | No | No |
| Private history access | Existing CM authorization | Existing authorized steward scope | Existing authorized admin scope |

A shared Discord panel must keep drafts bound to their initiating actor. Native drafts are bound to their authenticated session/actor. Losing a role invalidates later mutations even if the form was already open. Viewing a button is never authorization. No voting or self-case restriction is added.

## Ready notification and one-hour window

After owner finalization, verified numeric application and matching regenerated content, send the owner-tagged ROUND RESULTS READY notification with all current sanctions and effects. Its acknowledged send starts the exact revision's 3,600-second window. The UI shows the same notification ID, revision, countdown and current penalty summary.

Approve now or Hold / request changes works directly in CM and updates the same backend state as the Discord buttons. A linked owner reply in Discord pauses the timer. No owner response in either interface within the hour authorizes automatic validation. Mere viewing the native screen is not a response. Settings must not replace the user's authorized 3,600-second rule with a different silent timeout.

Persist the timer across restarts. A changed review/content revision invalidates old approval and requires a new verified ready alert/window. Owner response recorded at or before the deadline wins transactionally. Missing alerts or ambiguous alert delivery cannot start a guessed timer. Sunday 23:00 is the availability deadline, not permission to skip verification or shorten the hour.

## Delivery requirements

Reuse the consumer contract for ordered sending, pinned snapshots, stable delivery keys, nonce use, leases, rate limits, receipts and ambiguous-send reconciliation. Resume only from durable state after restart. Preserve the three-message results announcement and its real link to the first full-results message. Public poster carousels use persistent handlers and update the same message; protected individual/team and practice posters remain direct.

When CM is stopped, no delivery worker runs: display overdue work and resume safely on restart. This feed does not supply external unattended generation or an always-on CM host.

## Required acceptance evidence from VSC

Before reporting completion, provide the changed CM files, actual source-to-existing-app mappings, configuration instructions and the checks performed. Separate local preview checks from actual Discord and ACSM verification.

Verify at least:

1. Post Results sidebar item, live championship tabs and all six scoped sub-tabs.
2. Owner enters channel IDs, validates destinations and sees exact ordered text/poster previews.
3. First import lists historical archives without publishing them; malformed imports retain the prior valid snapshot.
4. Native Apply and Cancel work without Discord interaction, with shared history and no repeated numeric writes.
5. Role removal, unauthorized users, two actors, repeated clicks and restart do not bypass permissions or duplicate effects.
6. Combined sanctions, threshold resets, cancellation and manual ban states are correct; practice remains allowed.
7. Owner can finalize zero penalties and hold/approve from CM; timer responds to CM and Discord decisions and survives restart.
8. Stale results or failed ACSM writes block release; updated verified content invalidates prior timer/approval.
9. Actual ordered test delivery, real announcement jump link, permitted mentions only and working persistent poster navigation.
10. Recovery from partial delivery, ambiguous send and post-publication corrections preserves message identities and audit history.

Use a controlled non-production destination and fixture data for initial tests. Numeric ACSM live writes must be based on actual authorized decisions; do not create fake penalties in production to test the adapter. Document unavailable live verification honestly and expose its blockers in CM.
