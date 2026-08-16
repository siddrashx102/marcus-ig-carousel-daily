# Marcus Instagram Posting Routine

Runs every 5 hours. Every run does the same two things: **check what's already scheduled, and prepare the next thing.**

1. **Check scheduled posts.** For every row marked "Scheduled" in the sheet, ask Buffer if it actually went live yet.
   - Went live → mark it "Posted", text me the music suggestion for it.
   - Failed → mark it "Failed", alert me.
   - Still waiting on its own scheduled time → leave it alone.

2. **Prepare the next one.** Find the oldest row still marked "Not Ready." Just one per run.
   - Write its caption and generate its media (Carousel or Reel — method in the Reference section).
   - Come up with a music suggestion for it.
   - Hand it to Buffer, scheduled for its own Date at 9:00 PM IST.
   - Anything fails along the way → mark "Failed", alert me, move on.

That's it. No "today"/"tomorrow" logic — the sheet's Date column is the only thing that decides when a post actually goes live (Buffer holds it and fires it itself). This routine's only job is to keep feeding Buffer content faster than it needs it.

---

## Reference

**Credentials**: read from `.env` in this project directory (`C:\Users\siddr\OneDrive\Documents\Projects\digital-product\maras_accounts\baker_male_persona\.env`) — never ask the user for them.

**Sheet**: spreadsheet `1_kQX8A596S1dj3BEmOaBdy-IrqHZ84DkVEe_H53xXwc`, tab "Instagram Queue" (gid `2120158175`), via the Zapier Google Sheets connection. Columns: A=Day, B=Date (DD-Mon-YYYY, this row's own Instagram post day), C=Hook/Topic, D=Caption, E=Media URL (single video URL for Reel; comma-separated image URLs in order for Carousel), F=Status (Not Ready / Ready / Scheduled / Posted / Failed), G=Posted Timestamp, H=Error, I=Scheduled (TRUE/FALSE), J=Media Type ("Reel" or "Carousel" only), K=CTA, L=Pillar, M=Buffer Post ID, N=Music Suggestion.

**Buffer**: GraphQL `https://api.buffer.com/graphql`, `Authorization: Bearer $BUFFER_API_KEY`, channel `6a7611ab99afb443491dd3a3` (marcus.stoic.calm).
- Check status: `query($id: PostId!) { post(id: $id) { status sentAt error { message } } }` — `status` is one of `sent` (live), `error` (failed), `scheduled`/`sending` (still pending).
- Schedule: `mutation($input: CreatePostInput!) { createPost(input: $input) { __typename ... on PostActionSuccess { post { id status dueAt } } ... on InvalidInputError { message } ... on UnexpectedError { message } ... on LimitReachedError { message } } }` with `input: { channelId: "6a7611ab99afb443491dd3a3", text: <Caption>, assets: [{ video: { url } }] for Reel or [{ image: { url } }, ...] for Carousel (max 10 images — Instagram's carousel cap; trim/merge slides if the shot list produces more), mode: "customScheduled", dueAt: "<row's own Date>T15:30:00Z", schedulingType: "automatic", needsApproval: false, saveToDraft: false, metadata: { instagram: { type: "reel" for Reel, "post" for Carousel (NOT "carousel" — that enum value is rejected here; confirmed live 14-Aug-2026, Instagram determines carousel-vs-single from asset count alone, "post" with multiple image assets is what actually produces a real carousel), shouldShareToFeed: true } } }`.
- Cancel a post if ever needed: `mutation($id: PostId!) { deletePost(input: { id: $id }) { __typename ... on VoidMutationError { message } } }`.

**Cloudinary**: signed upload to `https://api.cloudinary.com/v1_1/$CLOUDINARY_CLOUD_NAME/{video|image}/upload`, signature = `sha1("public_id=<id>&timestamp=<ts>" + $CLOUDINARY_API_SECRET)`.

**Vapi**: `Authorization: Bearer $VAPI_PRIVATE_KEY`, `POST https://api.vapi.ai/call`, `phoneNumberId=$VAPI_PHONE_NUMBER_ID`, `customer.number=$VAPI_ALERT_TARGET_NUMBER`, transient inline assistant (no saved assistantId), model gpt-4o-mini, voice provider vapi voiceId Elliot, maxDurationSeconds 30.

**Telegram**: send-message tool, owner's DM by default.

**Failure alert**: Telegram (full detail — day, error, sheet link https://docs.google.com/spreadsheets/d/1_kQX8A596S1dj3BEmOaBdy-IrqHZ84DkVEe_H53xXwc/edit#gid=2120158175) + Vapi ("Alert. Instagram post for day <Day> <one-line reason>. For full error details, check the Telegram message. Goodbye.").

**Post-live alert**: Telegram + Vapi, both naming the day and reading out the Music Suggestion, telling the user to add it from their phone (Instagram's music picker only exists in the mobile app — this can't be automated, it's always a manual step).

**Carousel generation** (primary format — 26 of 28 days; reference `C:\Users\siddr\OneDrive\Documents\Projects\digital-product\maras_accounts\post_08082026\`, method only, not that folder's Mara branding):
1. 8-11 slide shot list: cover/hook → thesis/reframe → "here are N things" → numbered list points → a relevant attributed Stoic quote (Marcus Aurelius / Epictetus / Seneca) → payoff → close (engagement question + save-CTA). Full worked example in `post_08082026/Carousel_Post.md`.
2. Build each slide as HTML using the CSS template in `post_08082026/carousel/build_slides.py` (1080×1350px, Georgia serif, `#F3EEE4`/`#2B2A26`/`#8C6E4F` palette, numbered badges, quote styling) — watermark changed to `@MARCUS.STOIC.CALM`. Write to a temp folder, e.g. `C:\Users\siddr\AppData\Local\Temp\claude\carousel_<Day>\html\slide_NN.html`.
3. Render each to PNG: `capture-website "<html>" --output="<png>" --width=1080 --height=1350 --overwrite` (CLI, already installed, no browser needed).
4. Upload each PNG to Cloudinary in order, join the `secure_url`s with commas for the Media URL column.
5. Caption follows `post_08082026/Carousel_Post.md`'s exact formula (hook → thesis → numbered list restated → reframe → engagement question → save-CTA → SEO keyword block → 6-8 hashtags), written fresh from this row's actual Hook/Topic, CTA, Pillar.

**Reel generation** (secondary format — D1/D4 only; quality bar `reel_2_flow/`):
1. 3-4 scene shot list, hook → build → insight/resolution (same arc as reel_2's captions.srt), each scene's prompt including the literal line Marcus says.
2. Browser to https://labs.google/fx/tools/flow (logged in). New project. Per scene: type prompt, submit, click "Approve" if a cost dialog appears, poll every ~15s up to 5 min for generation, download the clip. Reference images for likeness: https://res.cloudinary.com/xqp3g1gq/image/upload/v1786691528/marcus_avatar_ref_1.png and .../v1786691536/marcus_avatar_ref_2.png.
3. ffmpeg concat the downloaded clips in order (same method as `reel_1/concat_list.txt`), burn captions from the scene script via a generated `.srt` (same as `reel_1/captions.srt` → `baker_reel_final_with_captions_sfx.mp4`).
4. Upload the merged file to Cloudinary — single Media URL.

**Music Suggestion** (both formats): mood/genre + 1-2 concrete example track/artist names commonly on Instagram, based on this row's Hook/Topic and Pillar — a starting point to search on the phone, not a guarantee of exact library availability.

Instagram only — no TikTok/YouTube/LinkedIn. Don't touch rows beyond what steps 1-2 naturally pick.
