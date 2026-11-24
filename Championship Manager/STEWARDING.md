# Stewarding Review and final-results release

## Review post

Add a text-only **Stewarding Review** post in Results, after Race Results and before Race Insights. Use the usual checked marker, short sentences, blank lines and readable player lists. It has zero posters and direct presentation. It contributes no images to the results-announcement carousel.

Use these sections when supported by the available evidence:

- **Practice observations**: relevant practice incident patterns, with the snapshot cutoff and sample context.
- **Race observations**: factual contact/incident patterns and unusually incident-heavy sessions or phases.
- **Race impact**: observed time loss or position changes linked to identified incidents where the timing/replay evidence supports that relationship.
- **Decisions by driver**: the organizer's sanctions, their scope and their verified application.
- **Championship consequences**: time/points changes that actually altered classification or standings.

Maintain a neutral, non-stigmatizing tone. Contact telemetry counts can be repeated or mirrored and do not equal unique crashes. A large count alone establishes neither fault nor deliberate conduct. Describe uncertainty and omit causal or blame claims that cannot be supported. Review and disciplinary wording stays factual, with no caustic jokes about sanctioned players.

The Results Announcement's condensed text includes a concise Stewarding Review section. Include the confirmed sanctions and any resulting changes to race/points outcomes. Link to the complete Results sequence in the existing prominent opening section. Its three-message structure remains unchanged.

## Organizer-supplied penalty types

The organizer's current list supersedes older descriptions in the reference screenshot.

| Machine type | Value | Effect |
| --- | --- | --- |
| time_penalty | 5 or 20 seconds | Add to the driver's official race time and reconcile the resulting official classification. |
| points_deduction | 10 points | Deduct 10 championship points through the verified official adjustment mechanism. |
| outstanding_penalty | Award of 1, 2 or 3 | Add the organizer-supplied amount to the active counter. Reset immediately at each threshold of three and retain the threshold history. |
| round_ban | Explicit affected round | A confirmed outstanding threshold of three triggers a round-ban decision/action record. |
| league_ban | League scope | The second confirmed maximum-outstanding threshold event triggers a league-ban decision/action record. |
| servers_discord_ban | Explicit server set plus Discord guild | Organizer-confirmed trolling, annoying behavior, childish/immature ranting or related stated conduct. Preserve the supplied reason and scope. |

The screenshot describes a five-second sanction for an isolated reckless move with significant pace impact, a twenty-second sanction for critical race impact, and a ten-point sanction for deliberate retaliation. These descriptions guide the organizer's decision. The bot does not infer intent or choose sanctions from crash counts.

The organizer supplies the decision list and confirms that review is complete, including an explicit empty list when there are no penalties. Time and point sanctions require verified updates in both ACSM and all affected text/visual publication data. Outstanding penalties and bans require durable history and explicit enforcement state.

## Release gate

The whole post-race Results sequence and its Announcement remain unavailable for publication until this chain is complete:

1. The organizer supplies and approves the final decision set, including explicit zero penalties when applicable.
2. CM applies each approved numeric adjustment through the actual supported ACSM result/championship editing mechanism.
3. CM re-reads the official race result and championship standings, verifies each effective adjustment and records the refreshed result fingerprint.
4. The producer regenerates affected classification, gaps, points, driver/team standings, review text and all dependent posters/forecasts from that verified state.
5. CM validates that the sequence cites the approved review revision and the same verified result snapshot. Only then can status become ready.

A scheduled time alone cannot override this gate. A review change invalidates an unpublished ready package until it is reconciled and regenerated. A review amendment after publication is a new review revision with explicit corrections to the existing Discord messages. Do not create an untracked duplicate announcement or repeat everyone merely because a decision was amended.

For numeric adjustments, `acsm_verified` is required. `not_required` is permitted only when the approved list contains no time or points penalty. The reference reader checks the release metadata; CM must verify the actual organizer confirmation and ACSM writes. A producer-written boolean does not constitute real organizer approval.

## Applying penalties in ACSM

The CM integration must inspect the real ACSM version, its supported result-editing operations and championship points mechanism before implementing writes. This feed does not assume an unverified API route or simulate a successful update. Never delete source session JSONs to implement a sanction.

Persist the before-state and a transaction record before the first write. Identify a numeric adjustment by league, round, session, driver key, decision ID and review revision. Retrying an acknowledged decision must not add another five/twenty seconds or subtract another ten points.

After every write, read back and compare the actual state. If a write times out, reconcile before retrying. If another administrator has edited the result, compare against the captured baseline and resolve the conflict. Partial success keeps the publication gated and resumes only unapplied operations. Record verified, failed and ambiguous actions separately.

Re-read the official classification and scoring rather than assuming a simple time sort across different lap counts or non-finishers. For points deductions, preserve the championship's actual team-scoring rule and propagate the official effect to both tables. Avoid applying a driver deduction a second time as a separate team deduction. A point sanction requires an effective numeric change, not only a textual note.

Some standings/penalty adjustments may live outside the downloadable race JSON. Retain the result and championship fingerprints necessary to verify the complete effective state. The integration must establish which ACSM edit fields implement time penalties and point adjustments correctly.

## Outstanding progression and bans

Maintain an append-only driver history across rounds, keyed by the stable driver identity. Record each confirmed outstanding state and every threshold event as a distinct event. Re-reading the same 3/3 decision must not produce a second threshold crossing.

An outstanding award can add **1, 2 or 3** at once, according to the organizer's severity decision. At each threshold of three, increment the durable maximum-event count and immediately reset the active counter to zero. Apply any remaining units of that same award to the new cycle. This carry-over interpretation preserves every awarded unit.

Examples: 0 + 3 reaches the threshold and leaves 0; 1 + 2 reaches the threshold and leaves 0; 2 + 2 reaches the threshold and leaves 1; 2 + 3 reaches the threshold and leaves 2. At the first confirmed maximum event, create the round-ban enforcement record and identify the affected round. At the second confirmed maximum event, create the league-ban record. The active counter resets immediately when reached; it does not wait for ban service. Keep the maximum-event history through every reset.

Time penalties, outstanding awards and points deductions may be combined for the same driver and the same case. Store each component with a distinct decision ID and a shared case ID. Apply all supplied components, recalculate the official numeric effect, and display every component together in the per-driver review. Never replace one component with another because the case already has a sanction.

New outstanding decisions use outstanding_mode=award. Historical state observations use outstanding_mode=snapshot and must never be replayed as a fresh award. The archived Round 4 observation remains a supplied resulting 2/3 state. It does not establish how many units were awarded in that particular case.

Reset, threshold and enforcement records are written in the same persistent transaction as the accepted award. Before applying an award, check its decision ID against the ledger. Repeated delivery, restart or ACSM retry must not increment the counter or trigger a ban again. Ban service, appeal and reversal remain explicit history events.

Require the organizer to identify a ban's effective scope and target round/league/server set. Record the approved decision and verified enforcement. Execute authorized round and league bans via the existing Blocklist workflow and schedule in [ACSM-Penalties-POST.md](ACSM-Penalties-POST.md). Servers and Discord ban remains manual. If enforcement is pending or fails, show that state accurately and retain the approved decision. Do not claim that a driver is banned until the relevant system acknowledges the action.

## Durable history

CM stores the authoritative ledger in its persistent database. Retain a record per case/decision with:

- Stable review, case and decision IDs; league/round/session and stable driver key.
- Incident reference, timing/replay evidence and neutral findings.
- Penalty type/value, supplied reason, organizer approval reference and effective scope.
- Review revision and timestamps; outstanding count and maximum-event count where confirmed.
- Before/after ACSM fingerprints, numeric deltas and per-system action receipts.
- Publication source revision, Discord message IDs and any later correction/appeal/reversal.

Corrections append superseding events. Keep prior decisions and receipts. The public repository contains the approved publishable review and its release metadata; private reports, credentials and moderator evidence remain in CM's controlled storage.

`stewarding/league-04/round-04.json` preserves the known historical Nordschleife decision as an archival observation. Its supplied 2/3 state is recorded directly, with no invented earlier incidents, resets, numeric adjustments or ban execution. It is not a new approved live action for CM to execute.

## Automated steward workflow

[STEWARDING_WORKFLOW.md](STEWARDING_WORKFLOW.md) specifies Sunday 15:00 CET report cutoff, Sunday 23:00 CET finalization, the role-authorized permanent panel, ENTRANTS-backed sanction wizard, automatic verified ACSM application and organizer-tagged results-ready notification. This deadline replaces the prior Sunday 20:00 rule for future live results.

## Authoritative owner decisions

[OWNER_DECISIONS.md](OWNER_DECISIONS.md) supersedes earlier recommendations on review finalization, publication control, cancellation, MEE6 report scope, manual bans and the one-hour owner-response timeout. Apply those decisions before implementing this workflow.
