# Marcus Instagram Carousel Routine (Cloud)

Single automated routine, runs daily in a Claude Code cloud environment. Posts one Instagram carousel per run for the Marcus persona (@marcus.stoic.calm), pulling from a pre-planned content queue.

This replaces an earlier local-machine routine ("Daily ig post marcus") — that one is being retired, this cloud routine is now the only one touching the queue. No locking/collision logic needed as a result — single writer.

## Persona reference
- Niche: stoic mindset / discipline, pain-point angle. Full tone/format notes: [content_format.md](content_format.md).
- Funnel product: "Unshakable" ebook, `https://thedigitalvault2025.gumroad.com/l/unshakable`.

## Sheet — single source of truth
Spreadsheet `1_kQX8A596S1dj3BEmOaBdy-IrqHZ84DkVEe_H53xXwc`, tab **"Instagram Queue"** (gid `2120158175`), via the Zapier Google Sheets connection. Link: https://docs.google.com/spreadsheets/d/1_kQX8A596S1dj3BEmOaBdy-IrqHZ84DkVEe_H53xXwc/edit#gid=2120158175

**Verified live columns (A-M — confirmed by direct read, do not trust any doc that lists a 14th "Caption" column, there isn't one):**
A=Day, B=Date (DD-Mon-YYYY, this row's own Instagram post day), C=Hook/Topic, D=Media URL (single video URL for Reel; comma-separated image URLs in order for Carousel), E=Status (`Not Ready` / `Ready` / `Scheduled` / `Posted` / `Failed`), F=Posted Timestamp, G=Error, H=Scheduled (TRUE/FALSE), I=Media Type (`Reel` or `Carousel` only), J=CTA, K=Pillar, L=Buffer Post ID, M=Music Suggestion.

Captions are never stored in the sheet — generated fresh each run, used only for the Buffer post.

All remaining Not-Ready rows (D4 onward) are Media Type=Carousel. Reel only applied to D1 (already Posted) and originally D4 (reset to Carousel in the format pivot) — so in practice this routine only ever needs to handle Carousel generation. No browser automation, no logged-in session dependency.

## Daily run — two sweeps every time

**Sweep 1 — verify Scheduled rows**
1. Read the Instagram Queue tab.
2. For every row where Status = `Scheduled`, query Buffer for that row's Buffer Post ID: `post(id) { status sentAt error { message } }`.
   - `sent` -> Status = `Posted`, Posted Timestamp = sentAt, Scheduled = TRUE -> Telegram alert naming the day and its Music Suggestion (add manually from phone — Instagram's music picker has no API).
   - `error` -> Status = `Failed`, Error = Buffer's message -> Telegram failure alert (day, error, sheet link).
   - still `scheduled`/`sending` -> leave alone, hasn't hit its own due time yet.

**Sweep 2 — prepare and schedule exactly one Not-Ready row**
1. Find all rows where Status = `Not Ready`. None -> stop, fully caught up.
2. Pick the single lowest-Day row.
3. Determine funnel stage from Day number: D1-D17 value/relate, D18-D21 soft teaser, D22+ full push (CTA = row's CTA column, links Unshakable).
4. Generate the carousel (below). Success -> Status = `Ready`. Failure -> Status = `Failed` (not back to `Not Ready` — a real failure needs a human, not silent retry) + Telegram failure alert.
5. If `Ready` -> schedule via Buffer `createPost`, `mode: customScheduled`, `dueAt` = this row's own Date column value, 9:00 PM IST (not "tomorrow" — its actual calendar day). Success -> Buffer Post ID written, Status = `Scheduled`. Failure -> stays `Ready`, Error written, Telegram alert.

## Carousel generation
1. 8-10 slide shot list (10 is Instagram's hard cap — trim/merge before hitting it, don't rely on last-minute trimming): cover/hook -> thesis/reframe -> "here are N things" -> numbered list points -> attributed Stoic quote (Marcus Aurelius / Epictetus / Seneca) -> payoff -> close (engagement question + save-CTA).
2. Fill `carousel_template/build_slides.py`'s `SLIDES` dict with that day's content (role guide is in the file's docstring), run it -> writes `carousel_template/html/slide_NN.html`.
3. Render each to PNG with the `capture-website` CLI (installed via the cloud environment's setup script, no browser needed). The environment runs as root, so Chromium needs the sandbox disabled — always pass it, don't wait to hit the crash first:
   `capture-website "carousel_template/html/slide_NN.html" --output="carousel_template/slides/slide_NN.png" --width=1080 --height=1350 --overwrite --launch-options='{"args":["--no-sandbox"]}'`
4. Upload each PNG to Cloudinary (signed upload, see below), collect `secure_url`s in slide order, join with commas -> that's the Media URL column value.
5. Write the caption using `carousel_template/caption_formula.md`'s formula, from this row's actual Hook/Topic, CTA, Pillar.
6. Write a Music Suggestion into column M: mood/genre + 1-2 concrete track/artist name commonly on Instagram, based on this row's Hook/Topic and Pillar — a starting point to search on the phone, not a guaranteed-available track. This is read later by the separate Post-Live Music Alert routine (see MUSIC_ALERT.md) — don't skip it.

## Buffer (GraphQL)
`https://api.buffer.com/graphql`, `Authorization: Bearer $BUFFER_API_KEY`, channel `6a7611ab99afb443491dd3a3` (marcus.stoic.calm).
- Status check: `query($input: PostInput!) { post(input: $input) { status sentAt error { message } } }` with `input: { id: <Buffer Post ID> }`. **Schema change, confirmed live 15-Aug-2026**: the old bare `post(id: $id)` shape now fails validation — Buffer wraps the id in a `PostInput` object, matching the `input:` convention their mutations already use. Independently re-verified against the live API before applying this fix.
- Schedule: `mutation($input: CreatePostInput!) { createPost(input: $input) { __typename ... on PostActionSuccess { post { id status dueAt } } ... on InvalidInputError { message } ... on UnexpectedError { message } ... on LimitReachedError { message } } }` with `input: { channelId: "6a7611ab99afb443491dd3a3", text: <caption>, assets: [{ image: { url } }, ...] (max 10, order matters), mode: "customScheduled", dueAt: "<row Date>T15:30:00Z", schedulingType: "automatic", needsApproval: false, saveToDraft: false, metadata: { instagram: { type: "post", shouldShareToFeed: true } } }`.
  **Critical, already-fixed bug**: `metadata.instagram.type` must be `"post"`, NOT `"carousel"` — that value is rejected by Buffer's API. Instagram determines carousel-vs-single purely from asset count; multiple `image` assets with `type: "post"` is what actually produces a real carousel. Confirmed live 14-Aug-2026.
- Cancel if ever needed: `mutation($id: PostId!) { deletePost(input: { id: $id }) { __typename ... on VoidMutationError { message } } }`.

## Cloudinary
Signed upload to `https://api.cloudinary.com/v1_1/$CLOUDINARY_CLOUD_NAME/image/upload`, signature = `sha1("public_id=<id>&timestamp=<ts>" + $CLOUDINARY_API_SECRET)`.

## Alerting
- Failure (Telegram only): full detail — day, error, sheet link.
- Post-live (Telegram only): day + Music Suggestion, reminder to add the track manually from phone (Instagram's music picker is mobile-app-only, not available via API).
- **Daily run summary call (Vapi)** — fires once, unconditionally, after both sweeps finish (success or failure, every run, not just on error). See below.

**Telegram mechanism**: raw Bot API, same pattern as Buffer/Vapi/Cloudinary — no connector. `POST https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage` with JSON body `{ "chat_id": "$TELEGRAM_CHAT_ID", "text": "<message>" }`. Send the body as proper UTF-8 JSON (or `--data-urlencode` if using curl) — a raw `-d` with an em dash or curly quote in the text fails with `400: strings must be encoded in UTF-8`, confirmed live during setup.

## Daily run summary call
Runs at the very end of every run, after Sweep 1 and Sweep 2 both complete — this is a status update, not a failure-only alert.

Persona: **"Alex, your content ops assistant"** — speaks like a real team member giving a routine daily report, not a robotic alert.

Build the script from what actually happened this run:
- Sweep 1: how many Scheduled rows were checked, and their outcome (e.g. "still pending, nothing new" / "day 2 confirmed live" / "day 3 failed, flagged").
- Sweep 2: which Day was prepared, its Hook/Topic, and outcome (scheduled successfully for its date at 9 PM IST / failed, with a one-line reason).
- If anything failed anywhere in the run, say so plainly and point to Telegram for full detail — don't read the full error aloud.
- Close naturally, e.g. "That's everything for today. Goodbye."

Example (all-success day): *"Hey, it's Alex with your Marcus content update. Today's scheduled posts are still pending, nothing new to report there. I prepared day 5's carousel — 'the comparison trap' — and it's scheduled to go live tonight at 9 PM. Everything ran clean today. That's it from me — goodbye."*

Example (a failure occurred): *"Hey, it's Alex with your Marcus content update. Day 3's post failed to publish — check Telegram for the full error. I prepared day 6's carousel — 'why discipline beats motivation' — that one's scheduled fine for tonight. That's today's update — goodbye."*

**Vapi call spec**: `Authorization: Bearer $VAPI_PRIVATE_KEY`, `POST https://api.vapi.ai/call`, `phoneNumberId=$VAPI_PHONE_NUMBER_ID`, `customer.number=$VAPI_ALERT_TARGET_NUMBER`, transient inline assistant (no saved assistantId), model `gpt-4o-mini`, voice provider `vapi` voiceId `Elliot`, `maxDurationSeconds: 60` (longer than the simple failure/post-live alerts elsewhere — this one has more to report).

## Environment variables (cloud environment config)
`BUFFER_API_KEY`, `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`, `VAPI_PRIVATE_KEY`, `VAPI_PHONE_NUMBER_ID`, `VAPI_ALERT_TARGET_NUMBER`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`. (Same values as this project's local `.env` — do not commit `.env` to this repo.)

## Setup script (cloud environment)
```bash
#!/bin/bash
npm install -g capture-website-cli
```

## Repo hygiene
This repo holds the routine's code/spec/templates only — never commit or push generated per-run content (rendered slide HTML/PNGs, etc.) back to it. The sheet, Cloudinary, and Buffer are the actual source of truth for what was posted; git history isn't needed for that and the cloud environment may not even persist commits between runs. Generated files can be written to a scratch/temp path and discarded.

**Never attempt any git write operation from within a run** — no commit, no push, no branch creation — even to fix a bug discovered in this doc. This environment's token is read-only against the repo by design; repeated attempts and retries just burn the run on a call that will never succeed. If something in this spec turns out to be wrong or outdated (an API schema change, a broken assumption, etc.), report it via the existing failure Telegram alert format (day/context, what's wrong, sheet link) and stop — don't invent a new alert type or notification channel for it. A human applies the actual fix to the repo.

## Related routine
A second, separate routine — **Post-Live Music Alert** — runs daily at 9:05 PM IST to confirm each day's post actually went live and prompt adding music from the phone. Spec: [MUSIC_ALERT.md](MUSIC_ALERT.md). It depends on this routine's Sweep 2 having written that day's Music Suggestion (column M) — don't skip that step.

## Scope
Instagram only — no TikTok/YouTube/LinkedIn. Don't touch rows beyond what Sweep 1/Sweep 2 naturally pick.
