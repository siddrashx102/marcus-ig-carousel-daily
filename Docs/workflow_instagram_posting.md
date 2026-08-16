# Instagram Posting Workflow — v6 (live)

## Trigger
Local routine (`Daily ig post marcus`), runs **every 5 hours** (changed from once-daily 9PM) — in this same Claude Code environment on this PC while it's on/awake, not an isolated cloud sandbox. There is no "today"/"tomorrow" targeting anymore. Two independent sweeps run every time, working through the backlog: **verify anything currently Scheduled** (Sweep 1), then **prepare + schedule exactly one more Not-Ready row** (Sweep 2). Content preparation throughput is now decoupled from the actual Instagram posting cadence — each post still only goes live on its own Date column's day, at 9:00 PM IST, because Buffer holds it until then regardless of when it got scheduled.

## Runs in this local environment
Confirmed it has `.env` access (reads Buffer/Cloudinary/Vapi keys from the project directory) and reaches Google Sheets via the Zapier connection, both proven across real runs. Browser-tool access for Google Flow generation is still unconfirmed — only matters for 2 of 28 days now (Reel is secondary format).

## Status vocabulary (v6)
`Not Ready → Ready → Scheduled → Posted` (or `Failed` at any step). Same states as v4, but selection logic changed — no longer date-gated, now backlog-gated.

## Sweep 1 — Verify all Scheduled rows
1. **Read** `Instagram Queue`. Find **every** row where `Status = Scheduled` (plural — several can be pending simultaneously now, since prep runs ahead of the calendar).
2. For each, query Buffer's `post(id: <Buffer Post ID>)` for `status`/`sentAt`/`error`.
   - `sent` → `Status = Posted`, `Posted Timestamp = sentAt`, `Scheduled = TRUE` → **post-live music alert** (Telegram + Vapi, see below — new in v6).
   - `error` → `Status = Failed`, `Error = <Buffer's error message>` → failure alert (Telegram + Vapi).
   - still `scheduled`/`sending` → leave as-is, no alert — hasn't reached its own due time yet.

## Sweep 2 — Prepare and schedule exactly one Not-Ready row
1. Find all rows where `Status = Not Ready`. None → do nothing, fully caught up.
2. Pick the single lowest-Day row. **Only one per run** — the 5-hour cadence is the pacing mechanism.
3. Generate media per Media Type (below), including a **Music Suggestion** (new column N — see below). Success → `Status = Ready`. Failure → `Status = Failed` (not `Not Ready` — a real failure needs a human, not silent infinite retry every 5 hours) + failure alert.
4. If `Ready` → schedule via Buffer `createPost`, `mode: customScheduled`, `dueAt = this row's own Date column value, 9:00 PM IST` — not "tomorrow," its actual calendar day. Success → `Buffer Post ID` written, `Status = Scheduled`, no alert (that comes later in Sweep 1, once it actually publishes). Failure → stays `Ready`, `Error` written, failure alert.

## Media Type — v5, strategic pivot to Carousel-primary

Content calendar redistributed: **Carousel is now the primary format (26 of 28 days), Reel is secondary (D1, D4 only — the two days with real footage already shot)**. All other Media Type values (Talking-head Reel, Silent B-roll, Multi-cut Interview, Screen-recording, Text-only) are retired — `Media Type` in both sheets now only ever holds `Reel` or `Carousel`. This also **removes the 5 manual-shoot alert days entirely** (D3, D17, D19, D23, D24 — formerly Multi-cut Interview/Screen-recording) since they're now Carousel, fully automatable.

Driven by finding `post_08082026/` — a separate, already-proven carousel production system (built for a different persona, "Mara," reusing the *method* not the branding): 11-slide HTML/CSS template (1080×1350, warm serif aesthetic), rendered to PNG, modeled on a 76K-follower account's exact caption formula. Zero generation cost, no video risk, no manual-shoot dependency.

**Carousel generation (primary):**
1. 8-11 slide shot list per the proven structure: cover/hook → thesis/reframe → "here are N things" → numbered list → Stoic quote slide (attributed) → payoff → close (engagement question + save-CTA).
2. HTML built from the `post_08082026/carousel/build_slides.py` CSS template, watermark changed to `@MARCUS.STOIC.CALM`.
3. **Rendered via `capture-website` CLI** (already installed globally, confirmed working live: `capture-website <html> --output=<png> --width=1080 --height=1350`) — no browser session needed for this step, pure CLI.
4. Each PNG uploaded to Cloudinary; URLs joined comma-separated into the Media URL column (new convention: Carousel = multiple URLs, Reel = single URL).
5. Caption follows the exact proven formula from `Carousel_Post.md` (hook → thesis → numbered list → reframe → engagement question → save-CTA → SEO keyword block → hashtags).
6. Buffer's `createPost` takes multiple `{ image: { url } }` assets with `metadata.instagram.type: "carousel"` — confirmed valid via schema introspection.

**Reel generation (secondary, unchanged from v4):** Google Flow browser automation + ffmpeg merge/caption, quality bar is `reel_2_flow/`. Still has the same open/unverified items as before (Flow lip-sync reliability, Local routine browser-tool access) — but now only matters for 2 of 28 days instead of the majority.

**Review gate: none.** Generated content auto-flips to `Ready` and posts on its scheduled day with no manual approval step, per your call.

## Music — new column N, "Music Suggestion"
Discovered: Instagram's music/audio picker isn't available through the web app or the API — only the native mobile app. So Buffer-published posts always go up music-less; adding a track has to be a manual phone step regardless of automation. Workaround: Sweep 2 writes a practical music suggestion (mood/genre + 1-2 concrete example tracks) into the new **Music Suggestion** column while generating each row's content. When Sweep 1 confirms a post went live, the post-live alert includes that suggestion so you can add it from your phone right away.

## Alerting (Telegram + Vapi)
- **Failure alert**: Telegram full detail (day, error, sheet link) + Vapi call, shortened, ending *"For full error details, check the Telegram message."*
- **Post-live music alert** (new in v6, success case): fires when Sweep 1 confirms a post actually published. Telegram + Vapi, both naming the day and the suggested music track/genre to add manually.

## What this does NOT do
- Does not touch TikTok, YouTube, or LinkedIn — Instagram only, pilot scope.
- Does not silently retry a failed row — a genuine generation/scheduling failure sets `Status = Failed` and alerts, staying out of Sweep 2's pick until you fix it manually. (Sweep 2 does move on to the *next* Not-Ready row each run regardless, so one stuck row doesn't block the whole backlog.)
- Does not add music to posts automatically — not possible via API, confirmed; it's a manual phone step every time, prompted by the post-live alert.

## Verified live (14-Aug-2026)
- Buffer `customScheduled`/`dueAt` scheduling mechanism proven working (D2's old b-roll test post, since cancelled once Carousel pivot landed).
- Buffer `deletePost` proven working (used to cancel that stale post cleanly).
- `capture-website` CLI proven working (rendered a real `post_08082026` slide HTML to PNG, 107KB, correct dimensions).
- D2 and D4 both reset to `Not Ready` / `Carousel` after the pivot (D4's old Reel content was the already-shot `reel_2`, which had already been published on Instagram once before this automation existed — reusing it would duplicate a real post, so D4 gets a fresh carousel instead). D1 stays untouched — already genuinely `Posted` through this pipeline.
- **First full carousel run, D2 (15-Aug):** correction found — `InstagramPostMetadataInput.type: "carousel"` (the enum value that looked right from schema introspection) is actually **rejected by Buffer's API**. `PostType` is a shared enum across every platform Buffer supports (`event`/`offer` are Facebook/Google-Business values, `thread` is Threads, etc.), not Instagram-carousel-specific — Instagram determines carousel-vs-single purely from **asset count**. Correct value for a multi-image Instagram post is `type: "post"`. The routine caught this itself (real API error → self-corrected) and I independently verified by querying the live scheduled post directly: **10 real Cloudinary image assets attached in order, correct caption, correct `dueAt`, `metadata.type: "post"`** — this is what actually produces a carousel, not the originally-assumed `"carousel"` value. Reference doc/prompt corrected.
- Also confirmed live: **Instagram's carousel cap is 10 images**, not the 11 the reference template defaults to — routine merged two list slides to fit, no content lost. Worth designing shot lists at 8-10 slides going forward rather than relying on last-minute trimming.

## Routine change needed (not yet applied)
The Local routine's schedule setting still says "Every day at ~9:00 PM" in the Routines UI — needs to change to **every 5 hours** to match this design. Can't be edited via any tool available here; has to be changed manually in the routine's settings panel.
