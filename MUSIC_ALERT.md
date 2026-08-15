# Marcus Post-Live Music Alert (Cloud)

Separate routine from the daily carousel routine (CLAUDE.md). Runs once daily at **9:05 PM IST** — 5 minutes after Buffer's fixed 9:00 PM IST post time — to confirm that day's post actually went live, then prompts adding music manually (Instagram's music picker is mobile-app-only, not reachable via any API — this step can never be automated away).

Doesn't touch content generation or scheduling — read-only against the sheet except for the two status fields it's responsible for closing out.

## Why this needs to exist
The daily carousel routine (CLAUDE.md) only re-checks Buffer once per day, the next time it runs (Sweep 1, ~9:00 AM) — so a post that goes live at 9:00 PM would sit unconfirmed, and you unprompted for music, until the next morning. This routine closes that gap same-day.

## Trigger
Daily, 9:05 PM IST (Custom time trigger, 5 min after Buffer's fixed post time — gives Buffer a small margin to actually publish before we check).

## Logic
1. Read the Instagram Queue tab (spreadsheet `1_kQX8A596S1dj3BEmOaBdy-IrqHZ84DkVEe_H53xXwc`, tab "Instagram Queue", gid `2120158175` — same sheet as CLAUDE.md, via Zapier).
2. Find the row where **Date = today** (IST). If Status is already `Posted` (rare — main routine's morning Sweep 1 must have already confirmed a previous day's stray row), skip, nothing to do.
3. If no Buffer Post ID on today's row, skip — nothing was scheduled for today (shouldn't normally happen if the daily routine is keeping pace, but don't error on it).
4. Query Buffer directly (don't trust the sheet's Status column, it may not be updated yet): `query($id: PostId!) { post(id: $id) { status sentAt error { message } } }` using today's row's Buffer Post ID. Same GraphQL endpoint/auth as CLAUDE.md: `https://api.buffer.com/graphql`, `Authorization: Bearer $BUFFER_API_KEY`.
5. **`status: sent`** — confirmed live:
   - Update the sheet row: Status = `Posted`, Posted Timestamp = `sentAt`, Scheduled = TRUE (same write the main routine's next Sweep 1 would have made — doing it here just closes the gap same-day; idempotent, no conflict if the morning sweep also touches it later and finds it already `Posted`).
   - Read that row's Music Suggestion (column M — written by the carousel routine's Sweep 2, see CLAUDE.md). If blank (shouldn't happen once CLAUDE.md's fix is live, but don't crash if it does — generate one on the fly from the row's Hook/Topic + Pillar instead).
   - **Telegram alert**: day, Hook/Topic, the Music Suggestion, and a reminder to open Instagram and add it now. Link to the sheet row.
   - **Vapi call** to your phone (see below): short, names the day and reads the music suggestion, ends telling you to check Telegram for the full text if needed.
6. **`status: error`** — failed to publish:
   - Update sheet: Status = `Failed`, Error = Buffer's message.
   - Telegram + Vapi failure alert (day, error, sheet link) — same pattern as CLAUDE.md's failure alerts.
7. **`status: scheduled` / `sending`** still — not live yet (Buffer running a little late). Do nothing, no alert — the next morning's Sweep 1 will catch it eventually. Don't retry within this same run.

## Vapi call
`Authorization: Bearer $VAPI_PRIVATE_KEY`, `POST https://api.vapi.ai/call`, `phoneNumberId=$VAPI_PHONE_NUMBER_ID`, `customer.number=$VAPI_ALERT_TARGET_NUMBER`, transient inline assistant (no saved assistantId), model `gpt-4o-mini`, voice provider `vapi` voiceId `Elliot`, `maxDurationSeconds: 30`.

- **Post-live script**: *"Your Instagram post for day \<Day> just went live. Suggested music: \<Music Suggestion, shortened to the genre/mood and one track name>. Add it from your phone now. For the full suggestion, check Telegram. Goodbye."*
- **Failure script**: *"Alert. Instagram post for day \<Day> failed to go live. \<one-line reason>. For full error details, check the Telegram message. Goodbye."*

## Telegram
Send via the Telegram connector (same as used in this session) — not a raw bot-token env var. Add "Telegram" in this routine's Connectors panel alongside Zapier.

## Environment variables (this routine's cloud environment)
`BUFFER_API_KEY` (read-only use here, same value as CLAUDE.md's routine), `VAPI_PRIVATE_KEY`, `VAPI_PHONE_NUMBER_ID`, `VAPI_ALERT_TARGET_NUMBER`. Same values as this project's local `.env` — do not commit `.env`.

## Connectors
Zapier (Google Sheets), Telegram. No Cloudinary, no capture-website — this routine generates nothing, only checks and alerts.

## Repo hygiene
Same rule as CLAUDE.md — this routine writes to the sheet only, never commits/pushes anything to this repo.

## Scope
Exactly one row per run — today's row only. Never touches other rows, never generates content, never schedules posts — that's the other routine's job entirely.
