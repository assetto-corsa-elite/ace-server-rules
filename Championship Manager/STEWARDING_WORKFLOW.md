# CM stewarding workflow for VSC integration

This is the functional integration contract. CM owns the actual UI, Discord handlers, database and ACSM adapter implementation.

## Weekly deadlines and results release

MEE6 handles report submission and the report workflow outside this CM integration. Players submit reports until **Sunday 15:00 CET** for the round just raced. The deadline and any late-report handling remain in MEE6; CM does not implement report intake or acceptance.

Reports are analyzed and stewards make the decisions. **Sunday 23:00 CET** is the operational deadline for all decisions, automatic application and availability of the final sequence. Replace the previous Sunday 20:00 publication rule with release driven by completion of the verified review. A fully verified sequence can become available earlier. The 23:00 deadline is not an additional waiting period.

The organizer-approved final decision set, numeric ACSM read-back, refreshed standings and regenerated publication files remain mandatory. An empty decision list must also be explicitly confirmed as the completed review. If owner finalization is missing, decisions are incomplete, writes are failed/ambiguous or posters are stale at 23:00, keep the sequence blocked and notify the configured super admin with the specific outstanding work. The deadline never implies that missing decisions were approved.

The owner explicitly finalizes the complete decision set in CM. CM attributes the supplied decisions and verifies their application. Report intake, report review tracking and late-report acceptance remain in MEE6/the existing process.

## UI configuration

Provide persistent guild-scoped fields for:

- Results channel ID.
- Announcements channel ID.
- Stewarding panel channel ID.
- Sanction summaries channel ID.
- Results-ready/admin alerts channel ID.
- League Stewards role ID.
- Super Admins role ID.
- Organizer Discord user ID for tagged ready/deadline notifications.

Connect the existing **ENTRANTS** database as the live driver source, including its stable driver keys, Discord user IDs, aliases, league/round membership and participation state. Reuse CM's existing update mechanism. A Discord display-name change must not create another driver. Retain historical identities even after removal from current entrants.

## Permanent steward panel

Create one persistent bot message in the configured stewarding channel and store its guild/channel/message IDs. Restore its handler after restart and update the existing panel when history changes. Surface a deleted/missing panel in CM for controlled repair.

Embed title: **LEAGUE STEWARDING**.
Description: `Sanction history and penalty application.`

List history entries with **player, incident reason, penalty, race date and round name**. Use Discord date/time timestamps. Show numeric application state and outstanding progression when relevant. Use an ordered, paginated history so the message remains readable as the ledger grows.

Example history row:

`DRIVER — ROUND NAME — <t:RACE_UNIX:F>`
`Reason: Blueflag infraction. Sanction: +20s and +2 outstanding.`
`Outstanding: 2/3 → threshold reached → 1/3. Round ban: ROUND NAME.`
`Application: ACSM verified / enforcement pending / failed, as applicable.`

Primary action button: **Apply a penalty**. History pagination may use Previous/Next. Keep application controls simple and the history factual.

Only **League Stewards** and **Super Admins** may activate panel actions. Check the interaction's actual guild member roles server-side on every button, select and modal submission, including Apply. Discord does not provide a per-role clickable property on a shared button. Use channel permissions for visibility where desired and enforce authorization in handlers. Reject unauthorized interaction ephemerally with `Only League Stewards and Super Admins can use this panel.` No draft, log or sanction mutation follows a rejected interaction.

## Private application wizard

Use an ephemeral wizard per steward so concurrent stewards do not overwrite each other's form. Bind drafts to actor, guild, round and version. Persist sufficient state to recover or cleanly reopen after restart. Expired interaction tokens must not erase an acknowledged decision.

### 1. Choose player

Show **SELECT A DRIVER** and a dropdown populated from the current round's ENTRANTS data. Paginate or search when more drivers exist than the platform permits in one select menu. Use stable keys as values and clear in-game names as labels. Show the selected round name/date. When multiple rounds could be targeted, obtain an explicit target-round selection in CM's context before applying.

### 2. Choose incident type

Show **SELECT INCIDENT TYPE** with these exact choices:

- Unsafe race start leading to a crash
- Squeezing a driver
- Divebombing
- Blueflag infraction
- Weaving (multiple defense moves)
- Brake checking
- Unsafe pit exit into drivers
- Unsafe track re-entry into drivers
- Any unnecessary reckless move leading to a crash
- Flipping @Vern7 upside down against his consent

This field records the incident classification. It does not determine a sanction automatically.

### 3. Choose sanction

Show **SELECT SANCTION** with these choices:

- 5 seconds
- 20 seconds
- 10 points deduction
- 1 outstanding penalty
- 2 outstanding penalties
- 3 outstanding penalties
- Round ban
- League ban
- Servers and Discord ban

For outstanding penalties and all ban choices, open a modal with a required **Reason** text field. For numeric time/points sanctions, retain the selected incident type and permit a factual optional detail. Bind the modal to the draft and actor. For bans, obtain the target round or explicit league/server/guild scope and retain the supplied reason. Describe severe/behavioral conduct through that reason field; preserve the ten incident-type choices above.

### 4. Review accumulated sanctions

Show **PENALTY SUMMARY** with player, round/date, each selected incident type, sanction/value and reason. Show the current outstanding counter, projected counter after all awards and any projected threshold/bans.

Buttons: **Add another penalty** and **Apply**.

Add another penalty keeps the same player/round and returns to incident type, then sanction. Retain the existing components. Seconds, points and outstanding may all coexist for the same case. Removing an accidentally added draft component can be handled through a clear draft-edit action in CM.

Apply validates the authorized actor again, refreshes the current entrant/counter state, and rejects a stale draft for refresh if another steward changed the same player's review. Commit the decision bundle once, with unique case/decision IDs, then publish its summary in the configured sanction-summary channel. Duplicate clicks reuse the accepted application result.

The authenticated Apply action is the validation of this decision bundle. The completed round review is a separate completeness state.

## Summary message and automatic application

The sanction-summary message is a per-case audit message. Include player mention, round/date, incident types, reasons, every component and status. Initial status is `Applying` until verified. CM applies the approved seconds and points automatically through the real ACSM editing mechanisms, then edits the same summary to `Applied and verified`. Record partial failures with actionable details and retry/reconcile them. A failed Discord summary send must not cause the accepted numeric penalties to be applied twice.

Outstanding units are added transactionally, with immediate reset at three and carry-over of surplus. First threshold creates the round-ban enforcement record; second threshold creates the league-ban record. Retain the lifetime threshold-event count and the current active counter. Replays of a decision never add units again. Execute authorized round and league bans on the Blocklist schedule in [ACSM-Penalties-POST.md](ACSM-Penalties-POST.md). Keep Servers and Discord ban manual. Practice remains allowed before the round-ban window.

Apply the numeric updates exactly once, verify official race and championship data, then regenerate dependent text/posters. Race time sanctions can change the finishing classification; point deductions can change both championship tables under the actual scoring rules. A completed race's original starting grid remains a historical fact. Future-grid eligibility changes arise from an explicit affected-round ban or other explicitly supplied grid decision; do not manufacture grid-place penalties from time sanctions.

## Stewarding Review post in Results

Text only, after Race Results and before Race Insights. Keep all applicable information through clear sections and player bullets.

For each sanctioned driver show:

- Native driver mention and incident type/reason.
- Seconds added, points deducted and outstanding units awarded.
- Counter before/after, threshold reached and any affected-round/league ban.
- Verified before/after finishing position, gaps and championship points where affected.
- Next-round grid eligibility consequence if an approved ban changes it.

Add practice/race accidentology when supported by evidence, with appropriate sample context and neutral wording. Keep crash/contact-record counts distinct. Link an incident to a gap/position change only when the evidence supports that relationship.

The Results Announcement includes a condensed per-driver sanction/impact summary and the prominent full-results link. Its two direct result posters and remaining-poster carousel use the updated final data.

## Organizer notification when the package becomes available

When the verified final sequence becomes ready, immediately send one notification in the configured Results-ready/admin alerts channel. Tag only the configured organizer user using an explicit user allowlist. This notification does not ping everyone.

Embed title: **ROUND RESULTS READY**.

Include round/date, ready timestamp, review revision, ACSM verification status, the ordered sequence summary and a short per-driver list of **all currently assigned sanctions**, including their time/points/counter/ban consequences. State `No penalties assigned` when the approved set is empty. Link to the sequence in CM's UI when that route exists, or show its stable ID; never invent a UI URL.

Use the actual stored draft/preview link for internal checking where CM supports it. Before publication the public Results jump link does not yet exist, so do not fabricate it. The results announcement obtains its jump link only after the full Results sequence is delivered.

Persist the notification message ID with the ready revision. Update it after an amendment and mark a stale sequence blocked while it is regenerated. An ambiguous notification send is reconciled through the normal delivery ledger. The notification gives the organizer a current verification summary; it starts the owner-only publication validation window defined in OWNER_DECISIONS.md. Automatic validation occurs after one hour only if the owner has not responded.

## Deadline monitoring and acceptance tests

Show report cutoff and finalization deadline in CM's round UI. Display the MEE6-managed report cutoff as context; do not add report-count tracking or a parallel report workflow. At the finalization deadline, notify the organizer of any blocker. If a package is already ready, show its ready state and previously sent notification. Never mark a write verified merely to satisfy the time limit.

Test role removal between form steps, two simultaneous stewards, entrants updates, dropdown pagination, multiple sanctions, mandatory reason modals, duplicate Apply, an ambiguous ACSM write, crash/restart, threshold resets, second maximum, missed deadlines, explicit no-penalty finalization, result-order/points changes and the tagged results-ready notification. The full sequence must remain blocked whenever an applicable finalization condition is unresolved.

## Authoritative owner decisions

[OWNER_DECISIONS.md](OWNER_DECISIONS.md) supersedes earlier recommendations on review finalization, publication control, cancellation, MEE6 report scope, manual bans and the one-hour owner-response timeout. Apply those decisions before implementing this workflow.

The final offense label is intentionally humorous and remains a selectable supplied classification. It creates no automatic sanction and makes no claim about an actual incident. In menus, @Vern7 is a plain-text label. Any actual public driver mention must use the stable CM identity binding, without bold wrapping; never guess a Discord ID from this label. Preserve original labels on historical decisions when the current offense list changes.
