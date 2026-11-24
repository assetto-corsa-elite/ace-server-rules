# Poster viewers with Previous / Next

## Visual treatment

Use CM's own native Discord bot messages: one rich embed with an image and a row of two buttons. Each click edits the same public message. The embed replaces the corresponding multi-poster block in the sequence and retains every original poster as an individually readable screen.

The screen heading uses the embed's native `title`, which Discord renders prominently in bold. Example: `RACE INSIGHTS | RACE GAPS (3/4)`. The client controls font size; the API provides no arbitrary title-size setting. Show a blue ACE accent, the original full-resolution poster and a compact `ACE / Page 3 of 4` footer.

Buttons are `Previous` and `Next`. Disable Previous on the first screen and Next on the last. Start at screen 1 and preserve source order. A reader can open the current poster at full resolution through Discord's image viewer.

The viewer is shared in the channel. Any member who can see and interact with the post can navigate; all readers see the resulting screen. Persist the shared page. This public behavior is intentional and must be clear in the CM preview.

## Which posts remain directly visible

| Location | Presentation |
| --- | --- |
| Practice Highlights / field report, one or two posters | Direct images |
| Full Pre-Race Briefing, two posters | Direct images |
| Race-day Announcement, two briefing posters | Direct images |
| Race podium and individual Race Classification | Direct images |
| Driver Standings and Team Standings | Direct images |
| Forecast, one poster | Direct image |
| Qualifying Report, three posters | Carousel at its original sequence position |
| Race Insights, four posters | Carousel at its original sequence position |
| Results Announcement message 1 | Condensed text, everyone and complete-results link |
| Results Announcement message 2 | Direct individual Classification, then Team Standings |
| Results Announcement message 3 | Carousel of every remaining Results poster |

Keep authored text in the message's normal content when that post contains text. The embed heading identifies the active screen, while the full text remains available above it. One carousel is one published message, not a new message for each image.

## Feed representation

Every post declares `presentation.mode` as `direct` or `carousel`. A carousel adds `title` and an ordered `screens` array. Each screen has a clear `label` and `attachment_path` referencing the corresponding existing `attachments` entry.

For carousels, `attachments` is the logical source-image list, not the set of files uploaded into a single Discord message. It can exceed ten images because only the active image is uploaded at any one time. The reference validator checks complete, ordered screen coverage and enforces direct presentation for the protected categories above.

The three-message Results Announcement remains exactly three messages. Message 2 keeps its two direct result images. Message 3 browses all remaining originals without collages, dropping posters or adding more publication messages. This replaces the former rule requiring combined pages above ten remaining images.

The archived examples now declare two Results carousels and one Announcement carousel. Their assets and poster design remain the existing original images.

## Native Discord implementation

Use a rich embed plus Action Row buttons in the supported standard message-component mode. Omit the `IS_COMPONENTS_V2` flag for this embed-based payload, because the Components V2 layout has different content/embed semantics. CM can implement this through its Discord SDK.

The reference `render_carousel(post, page, viewer_key)` returns a message fragment plus the single active image's upload descriptor. Use the already-validated local image bytes. Its image URL is `attachment://FILENAME`.

On initial creation, combine the normal `render` content/allowed_mentions payload with the carousel fragment's `embeds` and `components`, and upload that one image. Retain the normal renderer's allowed_mentions on creation so any authorized mentions work. On page changes, use the carousel fragment's empty allowed_mentions and preserve the existing message content. The reference helper does not implement Discord sending or event handling.

When editing, explicitly retain only the new active attachment, using the SDK's edit-attachment API. Upload and update its embed image reference in the same edit. Do not accumulate obsolete attachments or reuse an expired attachment URL. Pre-download/cache all images from the pinned GitHub commit for reliable browsing.

Acknowledge each button interaction within Discord's three-second deadline. Defer the message update when required, then perform the edit. Buttons use stable custom IDs `cm:viewer:VIEWER_KEY:previous` and `cm:viewer:VIEWER_KEY:next`, within the 100-character limit.

## Persistence and concurrency

Store viewer key, guild/channel/message IDs, sequence/post IDs, pinned source commit, revision, ordered screens and current page in CM's persistent database. Register a persistent component handler at startup. A short-lived in-memory collector is insufficient for a published league archive.

Bind the custom ID to its stored message and verify the interaction's guild/channel/message before acting. Serialize navigation per viewer, deduplicate interaction IDs and respect Discord rate limits. Record desired/applied page state so a failed or ambiguous edit can be reconciled with the actual message after restart.

A content revision does not replace the viewer's pinned assets while users are browsing. Apply an explicit update through CM's content-changed workflow. A deleted message is a visible reconciliation condition, not permission to recreate it automatically.

Page changes never send a new message, repeat everyone, replay driver notifications or advance publication order. Sequence completion occurs once the initial carousel message and its first image are acknowledged by Discord. Readers do not need to visit every page before the next scheduled post can publish.

If CM is temporarily offline, the last screen remains readable. Navigation resumes when the persistent handler is running again. A live CM implementation and real guild test are still required.

## Acceptance checks

Test the first/middle/last screens, disabled buttons, long screen labels, mobile and desktop reading, image enlargement, active-image replacement, concurrent clicks, bot restart, rate limits and a deleted message. Confirm that protected direct posters remain visible, the announcement still has three messages and every source poster is reachable in the expected order. Verify no repeated notifications during navigation.

## Official references checked

- https://docs.discord.com/developers/resources/message#embed-object
- https://docs.discord.com/developers/components/reference#legacy-message-component-behavior
- https://docs.discord.com/developers/components/reference#custom-id
- https://docs.discord.com/developers/interactions/receiving-and-responding
