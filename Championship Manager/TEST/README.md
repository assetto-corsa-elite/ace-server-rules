# League 04 / Nordschleife Round 4 — complete manual TEST package

This package contains **5 ordered sequences, 13 Discord messages and 17 unique PNG posters**. The main catalog imports all five as **draft**. It supplies content for CM preview/manual testing; it does not send Discord messages, change ACSM, apply sanctions or enable automatic publication.

## Reading and preview

Open [PREVIEW.md](PREVIEW.md) for every text and all 17 posters in publication order. The machine entry point is the parent [catalog.json](../catalog.json). [sources.json](league-04/round-04/sources.json) records the public session URLs, checksums, standings and scope limitations.

| Sequence | Messages | Posters | Depends on |
| --- | ---: | ---: | --- |
| `test-league04-r04-pre-race` | Practice Highlights; Forecast | 3 direct | None |
| `test-league04-r04-pre-race-briefing` | Full briefing | 2 direct | Practice and forecast |
| `test-league04-r04-race-day-announcement` | Race-day announcement | 2 briefing posters reused | Full briefing |
| `test-league04-r04-post-race` | Qualifying; Race Results; Stewarding Review; Race Insights; Standings; Next-Round Forecast | 12 unique | Race-day announcement |
| `test-league04-r04-results-announcement` | Summary; two direct result images; remaining-poster carousel | All 12 post-race posters reused | Full post-race delivery |

Qualifying uses a three-screen carousel; Race Insights uses four screens. The final announcement keeps exactly three messages: summary, direct classification/team standings, then a ten-screen carousel of the remaining posters. Practice, briefing, podium/classification, standings and forecasts retain direct images.

## TEST rendering and routing

Use [tools/render_test.py](tools/render_test.py), never the production renderer. The production reference renderer explicitly refuses TEST post IDs. The TEST renderer:

- Starts **every** outgoing message with exactly `TEST AUTOMATIC POST RESULTS`, including image-only messages and carousel pages.
- Uses plain driver display names and disables all user, role and mass mentions.
- Requires the actual guild's verified `d_` emoji binding; no guessed emoji ID is supplied.
- Keeps all content within Discord's 2,000 UTF-16-unit limit after adding the TEST prefix.
- Requires the real **TEST** delivery receipt for the first qualifying post before rendering the results-announcement jump link.

The logical `results` and `announcements` fields retain source categorization. For this manual TEST run, CM must route **every message only to its existing configured TEST channel**, showing that destination before sending. A missing TEST channel blocks sending; no channel ID is invented or committed. The draft statuses must stay draft. Dates in manifests describe historical race context and are not a new publication schedule.

CM must use the TEST renderer for creation and carousel edits, retaining its prefix and empty mention lists. Reuse persistent viewer handlers and the existing delivery ledger. No live Discord delivery or CM runtime integration is claimed by this content package.

## Data scope

Practice is the Results export of **21 November 2026 at 15:33 CET**: **6 drivers, 9 recorded laps, one classified best lap**, Andy Thompson **8:21.031**. It is an **event-session snapshot**, not a week-long practice leaderboard. A `999999999` best-lap sentinel means no classified time.

Qualifying and race use that event's official exports. The historical pre-race briefing retains its originally supplied settings; actual lap-record conditions can differ. The next forecast follows the archived season order, Portimao Round 5; sources document the differing live ACSM label.

The historic review's **Outstanding Penalty 2/3** is a resulting counter snapshot, not a fresh award. The package requests no sanction, counter update or ban execution.

## Offline verification

From the repository root:

```bash
python "Championship Manager/tools/feed.py" validate
python -m unittest discover -s "Championship Manager/tests" -v
```

The TEST regression checks cover every message and carousel page, prefixes, no mentions, length limits, draft exclusion from automatic delivery, sequence dependencies, the TEST-only results link and refusal by the production renderer. Synthetic IDs used inside offline tests are never delivery configuration.
