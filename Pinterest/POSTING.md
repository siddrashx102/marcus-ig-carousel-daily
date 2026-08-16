# Marcus Pinterest Posting (Proven Pipeline)

Standard format decided **2026-08-16**: native Pinterest **carousel Pins** (2-5 swipeable images), posted via **Pinterest's own v5 API** — not Buffer. Buffer's Pinterest integration only supports single-image/video Pins (confirmed via GraphQL schema introspection: `PinterestPostMetadataInput` has no multi-card fields). Zapier's generic `create_pin` action is the same — single `image_url` only.

Proven live 2026-08-16: pin `924926842246983748`, "3 Stoic Habits for an Unshakable Mind", `creative_type: CAROUSEL`, 5 images, board "Mindset & Mental Strength".

## Why carousel, not single-image or video

- Single-image pins work (also proven live: pin `6a817c28b7242320f39e21e2` via Buffer) but waste the multi-slide content already being produced for this pillar.
- Video (talking-head, Google Flow) is the eventual goal but blocked on a logged-in Google session this environment doesn't have — revisit later, see [Docs/routine_prompt_local.md](../Docs/routine_prompt_local.md) for the equivalent Instagram Reel gap.
- Carousel reuses the same slide-generation template already built for Instagram, just capped at Pinterest's real limit.

## Account

Pinterest: **thedigitalvault02** — boards `eBooks`, `Mindset & Mental Strength`, `Products you tagged` (board IDs below). Buffer channel `6a817b3dccaf649a67b70226` also exists for this account (single-image fallback only, not used for carousels).

## Pipeline

1. **Generate slides** (2-5 per pin): add/edit an entry in `carousel_template/build_pins.py`'s `PINS` dict, run it -> writes `carousel_template/html/<slug>/slide_NN.html`.
2. **Render to PNG**: `capture-website "carousel_template/html/<slug>/slide_01.html" --output="carousel_template/slides/<slug>/slide_01.png" --width=1000 --height=1500 --overwrite --launch-options='{"args":["--no-sandbox"]}'` — repeat per slide.
3. **Upload each PNG to Cloudinary** (signed upload, same credentials/method as the Instagram routine — see root `CLAUDE.md`'s Cloudinary section): `https://api.cloudinary.com/v1_1/$CLOUDINARY_CLOUD_NAME/image/upload`, signature = `sha1("public_id=<id>&timestamp=<ts>" + $CLOUDINARY_API_SECRET)`. Collect `secure_url`s in slide order.
4. **Create the Pin** via Zapier's Pinterest raw-request passthrough (connection already authorized, connection_id `02555faf-c19d-87eb-a0e7-c52e67d78c10`, title `thedigitalvault02`):
   - Tool: `execute_zapier_write_action`, `tool_name: "pinterest_make_api_mutating_request"`, `selected_api: "PinterestCLIAPI"`, `action: "_zap_raw_request"`.
   - Params: `method: "POST"`, `url: "https://api.pinterest.com/v5/pins"`, **`headers: {"Content-Type": "application/json"}`** (required — omitting this makes Pinterest reject the body as `"Invalid request body"`, confirmed live), `body`: JSON string (see shape below).
   - `fail_on_errors: "false"` while testing so the actual Pinterest error body comes back instead of a generic thrown error; flip to `"true"` once a pin's content is trusted.

```json
{
  "board_id": "<numeric board id, see below>",
  "title": "<pin title>",
  "description": "<pin description, include #hashtags>",
  "link": "https://thedigitalvault2025.gumroad.com/l/unshakable",
  "media_source": {
    "source_type": "multiple_image_urls",
    "items": [
      {"url": "<cloudinary secure_url slide 1>"},
      {"url": "<cloudinary secure_url slide 2>"}
    ]
  }
}
```

`items` must have 2-5 entries (Pinterest's own hard cap — confirmed via their public OpenAPI spec, `PinMediaSourceImagesURL.items.maxItems: 5, minItems: 2`). A successful response is HTTP 201 with `"creative_type": "CAROUSEL"` and a real pin `id`. Note: the first few `media.items[].images` in the response can come back empty (`{}`) right after creation — Pinterest is still processing those images asynchronously; they populate within seconds, not a failure sign.

5. **Board IDs** (fetch fresh via `channel(input: {id: "6a817b3dccaf649a67b70226"}) { metadata { ... on PinterestMetadata { boards { serviceId name } } } }` on Buffer's GraphQL API if boards change):
   - eBooks: `924926910911597106`
   - Mindset & Mental Strength: `924926910912102483`
   - Products you tagged: `924926910911597111`

## What's NOT automated yet

- No scheduling — every post above published immediately (`shareNow`-equivalent; the raw Pinterest API call is instant, there's no `dueAt`/queue concept in this flow yet). If timed posting is wanted later, either delay the API call externally (cron) or investigate Pinterest's own scheduling support.
- No sheet-backed content queue (unlike Instagram's "Instagram Queue" tab) — pins are hand-specified in `build_pins.py` per run. Worth adding a "Pinterest Queue" sheet tab if this becomes a daily routine, mirroring root `CLAUDE.md`'s Sweep 1/Sweep 2 structure.
- No verification/alerting step (no Telegram/Vapi confirmation that a pin actually stayed live) — add if this becomes unattended.
