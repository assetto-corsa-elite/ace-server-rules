# Automatic Result Post production requirements

Apply the narrative, whole-field coverage, team storytelling and caustic humour requirements in [EDITORIAL.md](EDITORIAL.md) to every new package.

## Sequence and composition

| Stage | Text content | Posters |
| --- | --- | --- |
| Practice Highlights | Whole-week practice snapshot, top drivers, fastest models, most laps, notable comparisons and team form | Highlights plus a readable field report when needed |
| Forecast | Historical form, drivers to watch, team battle, points scenarios, known unknowns | Driver and team sections, points/gaps, actual current-track imagery |
| Pre-Race Briefing | Important race settings and a compact forecast | Exactly two: Race Essentials; driver and team standings |
| Qualifying Report | Classified order, gaps, close fights, team performance and relevant preparation | Driver Report; Qualifying Highlights; Team Report |
| Race Results | Podium, classification, individual and team stories, points impact, supplied review decisions | Podium; complete Classification, with review decision when appropriate |
| Race Insights | SimResults top-five consistency, position progression, full-field and focused gaps | Consistency; Positions; Gaps; Top-Five Gaps |
| Championship Standings | Complete driver/team points, changes and meaningful gaps | Complete Driver Standings; complete Team Standings |
| Next-Round Forecast | Carry the story forward using prior rounds and the new standings | Driver and team sections with the actual next track |

The producer maintains the league's results history, team membership, aliases and verified driver identities. Weekly practice comes from Live Timing when available; an event's short practice session is a different snapshot. State the cutoff used. Reconcile each round to its actual session labels, circuit configuration and official result JSONs.

## Text

Write in English. Keep the established titles, section categories and thematic emojis. Every section begins with `{{emoji:checked}}` followed by its thematic Unicode emoji and bold heading. CM renders checked to the actual `d_` custom emoji.

Preserve the required level of detail. Total editorial volume is not capped. Keep sentences short, with one idea per line. Use blank lines between sections and bullet lists for individual results and team point summaries. Avoid dense paragraphs, tabs and four-space indentation that Discord renders as a code block. Use shallow indentation only when it clarifies a list. Split a detailed section across successive messages at the Discord limit; never remove pertinent content merely to shorten a package. Preserve a factual, lightly humorous racing tone. Connect stories to past practice and race results. Each rendered Discord message stays within 2,000 UTF-16 units. Split long posts at section boundaries and give each part a stable post ID/order when necessary.

Use stable driver tokens throughout all messages. Never invent or vary a Discord handle. Escape underscores in ordinary display text, such as `Burnout\_Baddies`. Native mention tokens remain outside bold formatting. The renderer inserts Discord mentions and custom emoji after all escaping.

Use Discord Unix timestamps. `t` renders an hour only, `F` renders date and time. Confirm the source timezone before calculating the Unix value. Duration and elapsed-race-minute values remain durations.

Only include race-review decisions supplied by the organizer or established official review. Telemetry contact records do not establish fault. Outstanding penalties do not imply an invented time or points adjustment.

## Posters

Use the official ACE logo and the established white/blue/black palette with restrained red accents. Keep a clear title, circuit and round. Use an editorial hierarchy, readable margins and enough visual space for circuit photography and car liveries. Tables should serve exact comparisons; photos and focal points should carry the visual identity.

Retrieve actual liveries from server skin previews when possible. Use real imagery of the correct circuit/layout. Preserve source credits. Keep the same factual detail as the established reports, including team performances when relevant. Forecast posters must contain a visible team section alongside driver content.

Render exact figures and charts with deterministic layout/plotting tools. Do not invent cars, liveries, circuit scenery, points or race events. Charts need clear driver identification, units, legends and a documented method. Distinguish reconstructed lap-time gaps from official finish gaps. Make all full-field charts readable at the delivered resolution.

## Checks before commit

- Check the source results, classification, points, gaps, aliases and team membership.
- Open and visually inspect every final poster for clipping, unreadable labels and missing team sections.
- Check UTF-8, mojibake, HTML entities, broken Markdown, underscores, section markers and all identity tokens.
- Render using CM bindings when available; verify final lengths and native Discord syntax.
- Validate asset hashes, byte sizes, PNG signatures, sequence order and explicit schedule.
- Commit assets, texts, manifest and catalog atomically after all checks pass.

Keep screenshots, admin credentials, private chat logs and raw driver database exports outside this public feed. Public posts and publication assets are sufficient for CM delivery.

## Announcement deliverables

Add the race-day 09:00 CET briefing announcement and the three-message results announcement described in [ANNOUNCEMENTS.md](ANNOUNCEMENTS.md). Every Results package must link its announcement posters explicitly. The full Results sequence remains the source of truth, and the announcement links back to its first delivered message.
