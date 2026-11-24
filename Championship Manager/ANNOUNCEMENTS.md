# Announcements and Results routing

## Channels configured in CM

The CM UI must expose two persistent input fields, **Results channel ID** and **Announcements channel ID**, scoped to the Discord guild. Validate each ID, the target guild and the bot's send/attachment/mention permissions. Store the IDs in CM's local configuration. Repository messages refer to logical keys `results` and `announcements`.

All full publication sequences go to `results`, including practice highlights, forecasts, the full pre-race briefing, qualifying, race results, insights, standings and next-round forecast.

## Race-day announcement

Add a separate `race_day_announcement` sequence in `announcements`, scheduled on the actual race date at **09:00 CET (UTC+01:00)**. Encode its exact date and offset in `scheduled_at`; do not assume every race is Saturday. This adds a confirmed race-day cadence while leaving the full Results pre-race briefing's time independently configured.

Its single message starts with `@everyone`, then gives the important briefing settings, localizable schedule, pit window, relevant rules and a compact forecast. Attach the two related briefing posters in order: Race Essentials, then driver/team standings. Keep checked-section tokens and the same native driver mappings as other posts.

## Results announcement: exactly three messages

After CM has successfully completed the entire Results sequence, send a `results_announcement` sequence in `announcements`. No additional delay is required. Its explicit scheduled time is the earliest permitted time, and `requires_sequences` is the completion gate. Persist each announcement message in the normal delivery ledger.

1. **Condensed text**. Prefix with `@everyone`. Place the complete-results link in the first section, directly below the title, before the summary. Use the wording `➡️ **[Find the complete results in Results](JUMP_URL)**`, with a checked marker and a restrained chart emoji. Include the podium, key individual/team performances, championship impact and relevant supplied race-review decisions.
2. **Individual and team result posters**. An image-only message containing the individual Race Classification poster first, then the Team Standings poster. This explicitly defines the individual/team selection for the imported package.
3. **All remaining result-sequence posters**. A carousel message immediately after message 2. Include every remaining poster from the full Results sequence, preserving its original post/attachment order. Omit the two images already sent in message 2, so every source poster appears exactly once across messages 2 and 3.

Message 2 keeps its two direct images. Message 3 becomes a single embed carousel containing all remaining source posters, following [CAROUSELS.md](CAROUSELS.md). Only its active image is uploaded at a time, so the logical screen count can exceed ten without merging the posters.

Send the three messages back-to-back under the same destination queue lease. Respect Discord rate limits without inserting an editorial delay or allowing another CM sequence to interleave. A failure pauses this announcement; restart resumes from its first unacknowledged message without re-pinging an acknowledged summary.

## Link to the first complete-results message

`link_targets.results_start` identifies the full Results sequence and its **first post**, including qualifying if that is the opening message. Resolve the exact delivered message ID from CM's persistent ledger for the configured Results channel. Construct `https://discord.com/channels/GUILD_ID/RESULTS_CHANNEL_ID/MESSAGE_ID` and bind it to `{{link:results_start}}`.

The URL is runtime data. Never guess a message ID or substitute a channel-only link. If the source is incomplete or its first message ID is unavailable, keep the announcement waiting and expose the missing dependency in CM. The reference renderer rejects unresolved or malformed jump URLs. Channel bindings used for a started sequence remain frozen through completion and are retained in the ledger, so a later UI change cannot redirect its deep link.

## Everyone rules

| Message | Everyone ping |
| --- | --- |
| First message of the Practice Highlights sequence in Results | Yes |
| Any following practice/forecast message | No |
| Full pre-race briefing in Results | No |
| Race-day 09:00 announcement | Yes |
| Qualifying, race, insights, standings, next forecast in Results | No |
| Results announcement message 1 | Yes |
| Results announcement messages 2 and 3 | No |

`mention_everyone` is explicit in every post. The renderer inserts the literal `@everyone` only for the authorized first messages and enables `allowed_mentions.parse=["everyone"]` only for those messages. Other messages use an empty parse list. Driver mentions retain their explicit user allowlist. Do not add a role mention or a ping in media follow-ups. Preview the notification intent in CM's UI.

Two archived Round 4 announcement examples demonstrate all fields, attachment references and the source link dependency. They are excluded from automatic sending like the other historical imports.
