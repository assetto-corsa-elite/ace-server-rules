# Publication feed audit - 24 November 2026

## Verified scope

The audit covers the repository content, its reference reader/renderer, schemas, publication contract and archived Round 4 examples. CM's application repository, running UI, database and Discord worker were not supplied for this task. Their implementation and end-to-end behavior remain unverified.

Four archived sequences contain ten Discord messages, eight text templates and fourteen unique PNG posters. Twenty-eight attachment references include the deliberate reuse of those images in the announcements. The catalog has zero ready sequences. The examples demonstrate publication structure; their presence does not activate a scheduler.

## Corrections applied in this audit

| Finding | Correction |
| --- | --- |
| Content volume was being confused with readability | Preserve detail; require short sentences, blank lines and structured lists. Split messages at Discord's content limit. |
| Code-block indentation could pass text checks | Reject tabs and four-space indentation at line starts. Ordinary bullets remain valid. |
| Circular sequence dependencies could wait forever | Detect and reject dependency cycles. |
| Announcement media could silently omit or reorder an image | Require exact source coverage, exact order and the two result posters first. Explicit image roles identify individual classification and team standings. |
| A complete-results link could point to another round's source sequence | Require a post-race source in the same league/round and its first post as the link target. |
| A race-day announcement could be scheduled at the wrong local time | Ready race-day announcements require race_date and 09:00 CET on that date. |
| A ready sequence could omit a publication stage | Validate phase/category compatibility and completeness for ready sequences. Detailed stages may span multiple messages. |
| Completed sequences could remain in the planning candidates | Exclude sequences already recorded complete by CM. |
| Configuration integrity could be partially declared | Require hashes for all three runtime configuration files. |
| The everyone prefix consumed additional content space | Include its length when validating the 2,000-unit rendered message limit. |
| Inherited test methods ran twice | Remove duplicate discovery; add targeted audit regressions. |

Twenty-two distinct regression tests pass. All four manifests also pass the JSON Schema check. PNG signature, declared size and SHA-256 checks pass. Native Discord rendering has been simulated using example bindings; it has not been verified against a live guild.

## Remaining work before autonomous operation

### 1. Producer scheduling and delivery to GitHub

Friday/Sunday cadences are configuration and documentation. No unattended ChatGPT/Codex job, generation runner or GitHub-writing scheduler has been installed by these repository commits.

A real producer trigger must author and verify text and posters, collect the correct weekly practice/result snapshot, wait for race-review completion, and commit a complete ready sequence. It needs durable access to the sources, prior-round history and GitHub. A failure must be visible and retried without releasing partial content. A content publication time and the generation start time are different settings.

Historical context in this feed currently contains Round 4 examples and prior-round references in their text. Complete Round 1-3 datasets and the full league calendar have not been imported into a machine-readable history store. Source ingestion must retain that history and account for changed track limits, reset practice statistics and changes of car/team. Current Portimao practice needs its fresh cutoff and current limits when produced.

### 2. CM integration, UI and persistent state

Implement the previously reserved integration stage in CM:

- GitHub snapshot polling or pull, pinned commit loading, validation and cached assets.
- The two channel ID fields, per guild, with permission checks.
- Connection to CM's existing driver database and verified destination emoji lookup.
- Ordered previews, poster thumbnails, scheduled local times, blockers and delivery history.
- Persistent queue, per-destination locking, message IDs, retries, rate-limit handling and restart recovery.
- First-message jump URL resolution before the results announcement.
- Controlled handling of edited content after delivery and ambiguous sends.

The reference feed program validates, renders and plans. Sending Discord messages and maintaining the delivery ledger belong to this CM implementation.

### 3. Round calendar and release conditions

Each new live round needs a confirmed race date, explicit publication timestamps, current race settings, source cutoff and finalized review. Race-day announcements are fixed at 09:00 CET. The full pre-race briefing in Results still has no agreed recurring publication time.

League 04 runs in winter, with CET equal to UTC+01:00. If reused for summer events, explicitly choose between fixed CET and French local time before generating timestamps. The current race-day validator implements the requested fixed CET time.

### 4. Runtime bindings and acceptance tests

Discord user IDs, the actual usable d_ emoji ID and destination channel IDs remain unset in this public feed. CM must resolve them from its own database/configuration. Preview with the real guild before enabling live delivery.

Acceptance tests must cover a long structured post, native driver/custom-emoji rendering, all three authorized everyone cases, both channels, the three-message announcement, its exact jump link, image order, rate limiting, a restart midway through sending and an ambiguous send. Verify permissions and destination attachment-size limits against the real bot and guild.

### 5. Validation execution

The committed checks are runnable locally and by the future producer. A GitHub Actions validation workflow has not been installed. The producer must run the checks before publishing; CI can subsequently enforce the same checks on repository changes.

## Editorial rule confirmed by ACE

The volume of information is not the problem. Do not remove pertinent analysis or team content merely to make posts shorter. Use short sentences, explicit line breaks, separate sections and shallow lists. A detailed package can contain successive messages with stable IDs and contiguous order. Only the first authorized message receives everyone; continuations do not.

## Carousel extension

Feed metadata now declares direct/carousel presentation. The reference code validates screen coverage and builds one-image embeds with Previous/Next buttons. The actual persistent handlers, edit operations and real-guild checks belong to the pending CM implementation. See CAROUSELS.md.
