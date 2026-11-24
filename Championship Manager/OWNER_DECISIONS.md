# Owner decisions - authoritative workflow and rights

These decisions supersede conflicting earlier recommendations in this directory.

## Identity and permissions

Use the configured organizer Discord user ID as the **owner identity**. Compare actual user IDs, not display names or a generic admin permission.

| Action | Authorized actor |
| --- | --- |
| Attribute a decision through Apply a penalty | League Stewards or Super Admins |
| Cancel an attributed penalty through Cancel a penalty | Super Admins |
| Close/finalize a round review | Owner only |
| Approve, hold, advance, resume or replay publication | Owner only |
| Configure sequence/message destination channel IDs | Owner through CM's existing UI |
| Browse public poster carousels | Members able to view/interact with the message |

The person using the sanction UI is responsible for the decision. Do not add a steward-voting requirement or a rule forbidding decisions on one's own case. Recheck the applicable roles or owner identity on every interaction.

Report submission, evidence collection, report edits, late reports and their handling are managed by **MEE6 and the existing steward process**, outside this integration. Sunday 15:00 CET remains the contextual report deadline. CM's UI attributes the decisions already reached; it does not rebuild the MEE6 report workflow or infer consensus from it.

## Permanent panel

Keep the sanction history with player, reason, penalty, race date and round name.

Buttons:

- **Apply a penalty** - League Stewards and Super Admins.
- **Cancel a penalty** - Super Admins.

Use private actor-bound wizards. Unauthorized users receive an ephemeral denial. Public button visibility does not replace server-side authorization.

## Duplicate-case warning

Before Apply, warn when the selected round/player and supplied report or case reference match a decision already attributed. Show the existing case, actor, sanctions and state. The actor may acknowledge and continue for a deliberate additional decision; a retry of the same accepted operation must reuse its idempotency key and never apply twice. Do not invent a MEE6 integration: use an existing case reference when available or show potentially matching local cases as a warning, without claiming they are confirmed duplicates.

## Cancel a penalty

1. Select player from ENTRANTS and retained historical identities.
2. Select the exact active penalty to cancel. Label entries with round/date, incident type, sanction/value, case ID and application status. A bundle's separate components remain individually identifiable.
3. Open a required **Reason for cancellation** modal.
4. Show the selected sanction, supplied reason and projected reversal effects.
5. Press **Apply**. Revalidate Super Admin role, decision state and draft revision.

Append a cancellation event with actor, reason, timestamp and a unique cancellation ID. Mark the original decision cancelled without deleting it. Repeated Apply or retries reuse the accepted cancellation.

If the original time/points adjustment was applied, automatically reverse that exact component through ACSM and verify read-back. Preserve every other sanction on the player/case. An ambiguous in-flight application must be reconciled before reversal. Persist before/after snapshots and receipts, and update the same sanction-summary message.

Cancellation invalidates unpublished affected results until regenerated and verified. For already-published results, create a tracked correction to their existing messages and posters, subject to owner publication control. Do not silently create another full sequence or repeat everyone.

Preserve outstanding history and **Max outstanding reached X/2** events. Do not erase completed cycles or automatically lift a manual ban when cancelling an older decision. Show the proposed current-counter effect from the decision ledger before confirmation. A correction to a completed-cycle history entry or manual ban is an explicit owner-controlled administrative action, rather than an inferred consequence of ordinary cancellation.

## Outstanding and manual bans

Awards may be 1, 2 or 3. Each reached maximum of three immediately resets the active counter to zero; surplus units carry into the next cycle. Persist the completed-cycle history as **Max outstanding reached 1/2**, then **2/2**.

At the first maximum, surface the required round-ban action for manual enforcement. At the second maximum, surface the required league-ban action for manual enforcement. The counter reset does not wait for that manual action. CM records ban decisions and their manual enforcement state; time/points application and outstanding progression are automated, while ban execution is manual.

Practice remains allowed under a round ban. The remaining ban access mechanics are outside this integration. They must not become an assumed automatic server/Discord ban adapter or a dependency on a new access-control implementation.

## Owner finalization and publication window

The owner alone finalizes the round's complete decision set, including explicit zero penalties. A role-held Apply approves its individual decision bundle, but does not finalize the round. Verified ACSM numeric updates and refreshed publication assets remain required.

When the verified package becomes available, send the existing owner-tagged ready notification with its complete current sanction summary. Start a **one-hour publication validation window** from the acknowledged notification send time for that exact ready revision. If delivery is uncertain, reconcile it before starting the timer. The ready alert must offer owner-only **Approve now** and **Hold / request changes** actions, without changing the simple steward panel.

- Owner clicks Approve now: approve that ready revision immediately.
- Owner clicks Hold / request changes: pause automatic validation.
- Owner replies to that ready notification: count it as an owner response and pause automatic validation pending an explicit owner decision. Unrelated messages elsewhere do not affect the window.
- No owner response within one hour: automatically validate that exact ready revision and let CM publish its ordered Results sequence, then its dependent announcement.

The owner has explicitly authorized this timeout behavior. Store an audit event identifying the mode as **automatic after one hour without owner response**, distinct from explicit owner approval.

A changed review or result revision invalidates the previous ready state, approval and timer. Regenerate and verify the package, send/update the corresponding ready notification with a fresh tracked send/acknowledgement for the new revision, then start a new one-hour window. Persist response timestamps, state and deadline so restart does not shorten or reset the existing window.

Resolve an approval/hold versus timeout race transactionally under the same publication lock. An owner response recorded at or before the deadline wins over automatic validation. Immediately before the first send, recheck the review/result revision, owner response state and any cancellation/reconciliation blockers.

Sunday 23:00 CET is the deadline for decisions, application and **package availability**. A package becoming available at 22:50 can automatically validate at 23:50 when the owner has not responded. Keep that separate from the availability deadline.

## CM destination fields

VSC must expose channel-ID fields in CM's existing UI for every configurable sequence/message destination required by the spec. Include Results, Announcements, steward panel, sanction summaries and owner notifications. Map each sequence/post to a logical destination key; permit owner-configured overrides when individual destinations are needed. Resolve and freeze the actual IDs for a started sequence so links and resume behavior remain consistent.

CM's existing application access/authentication and unrelated bot configuration are outside this task. Reuse them rather than creating another configuration-permission subsystem.

## Implementation acceptance checks

Verify authorization on each button, select menu, modal submit and final Apply, including role removal during a wizard. Drafts belong to their initiating actor; another user cannot continue them.

Check cancellation during pending ACSM application, repeated Apply, concurrent steward decisions and restart after a partially verified reversal. Keep accepted events and audit history intact.

Check Approve now, Hold, a linked owner reply, no response for 3,600 seconds, restart during the window, changed ready revision, uncertain notification delivery, and a response racing the deadline. A failed or stale package cannot be released by timeout.

The repository supplies this contract and the reference feed checks. VSC must implement the real Discord handlers, persistent timer, permissions, cancellation transaction and ACSM adapter in the existing CM application.
