---
name: basketball-score-clipper
description: Find made-basket timestamps in local or NAS basketball videos and export a chronological table and SRT markers. When explicitly requested, curate and edit verified highlights with player coverage, court audio, songs and beat alignment. Default to timestamps only.
---

# Basketball basket timestamps

Default outcome: a table of when the ball enters the hoop on the original video
playback timeline. Keep the existing `$basketball-score-clipper` invocation name.
Do not create previews, clips, montages, or editor projects by default. Do not
inspect the gather/release or tune export settings for a timestamp-only request.

## Runtime and inputs

Resolve this folder as `SKILL_DIR`. If `runtime.json` exists, use its `python`
and prepend its `bin_dir` to PATH. Otherwise use Python and tools on PATH.
Read the video directly from its local/NAS path. Leave originals unchanged;
write event JSON, optional review images, and the final Markdown table plus SRT marker file to a
separate output folder. Do not copy or transcode a whole video to get started.
Inspect duration, rotation and timing once; record `source_duration` and scanned
ranges to distinguish complete and partial analysis. Never infer timestamps from
the filename or wall-clock recording time; use actual presentation timestamps.
Reuse existing events and reviewed evidence for the same source when available.
Reuse avoids rescanning; it does not establish that an old acceptance is correct.
When producing highlights, recheck each selected attempt and the rendered basket.
Treat user-reported misses as exclusions until the disputed attempt is resolved.

## Fast timestamp workflow

1. View representative frames to confirm camera stability and the hoop ROI in
   displayed-frame pixels. Check frames across the requested range, not just the
   beginning. If the hoop moves, partition by stable ranges or use visual review;
   do not run a fixed ROI across moving-camera footage.
2. For a stationary hoop and a visible orange ball, run the existing CPU detector
   directly on the source:

   ```bash
   python3 "$SKILL_DIR/scripts/detect_fixed_camera.py" \
     --input /absolute/source.mp4 --hoop-roi x,y,width,height \
     --output /absolute/output/candidates.json --progress
   ```

   Keep the default frame step of 1: indiscriminate temporal subsampling may miss
   the brief crossing. The detector already limits image processing to the hoop
   neighborhood; no GPU or encoding is required. Video decoding and NAS reads
   still take time. Reuse a completed scan instead of repeating it for formatting.
3. Batch review small hoop crops around candidate timestamps, initially about
   0.7 seconds before through 0.5 seconds after each candidate, using consecutive
   source frames. Expand only ambiguous cases. No review MP4 is needed. Use
   剪映 only if explicitly requested or another viewing method is insufficient.
4. A make requires a downward entry through the opening followed by continuation
   through/below the net. A side pass or rim bounce is not sufficient. Save
   `result: made` and `review.status: accepted` for confirmed events, `miss` or
   `rejected` for false positives, and leave ambiguity pending. Confidence alone
   does not confirm baseline candidates.
   A ball falling in front of the net can overlap it in a two-dimensional crop.
   Net movement or a below-rim ball alone is insufficient: follow the same ball
   through the opening and its exit. Expand the view when this is ambiguous.
5. Set `basket_entry_time` to the first observed frame where the descending ball
   enters the rim opening; set `entry_time_basis: observed_frame`. Preserve
   `score_time` as the detector's later confirmation time. If only a bracketing
   interval can be identified, record an estimated entry time with
   `entry_time_basis: estimated` and state the uncertainty in `review.notes`.
   Never relabel a below-rim confirmation timestamp as an exact entry frame.
   All times must be original source playback seconds; add any proxy offset.
6. Sort per source and remove duplicate observations of the same basket using
   evidence, not a broad time cutoff that can erase separate attempts. Export:

   ```bash
   python3 "$SKILL_DIR/scripts/export_timestamps.py" \
     --events /absolute/output/reviewed-events.json \
     --output /absolute/output/basket-timestamps.md \
     --srt /absolute/output/basket-markers.srt --duration SOURCE_DURATION_SECONDS
   ```

   By default only visually accepted makes appear. `--include-pending` appends a
   separate pending table; these must not count as confirmed baskets.
7. Deliver the table inline and link both Markdown and SRT files. SRT contains
   one-second subtitle blocks starting at each entry time (clamped to the next
   marker and video end). These are subtitle-based location markers, not native
   flag markers. Keep ambiguous events out of this SRT. Use a separate SRT for
   each source; never mix different video time origins. Read
   [references/jianying-markers.md](references/jianying-markers.md) for import.
   The original video must start at timeline zero with its original speed and
   no preceding edits; otherwise markers need an explicit time mapping. Use columns for sequence,
   source, HH:MM:SS.mmm, seconds and timing basis. State analyzed duration/ranges
   and pending count briefly. If no makes are confirmed, say so; do not invent
   entries. A partial scan must not be presented as the complete match. Baseline
   candidates may miss baskets; do not claim full recall without evaluation.

## Corrections and explicit highlight requests

If a user reports a wrong basket, resolve which source event they mean. In a
countdown, playback position and rank label differ: the seventh segment of a
Top 10 is NO.04, whereas NO.07 is the fourth segment. Ask for the label or time
when the reference is ambiguous; do not silently choose one interpretation.
Remove the disputed event from the selection, preserve its previous review,
and update the authoritative event record and affected table/SRT/video outputs.
Do not describe the remaining old records as newly reviewed.

For event fields read [references/event-schema.md](references/event-schema.md).
When a montage uses an enlarged slow-motion pane, follow the ball-handling
attacker through the finish, with smooth reframing and enough room for the body,
ball and release. In a split layout, retain the wide view for basket context.
Use the replay-framing guidance below and verify the actual rendered crop.
Only when video output is explicitly requested, read
[references/clipping-workflow.md](references/clipping-workflow.md). For Top N
selection, player balance, music, mixing, beat alignment or a montage revision,
also read [references/highlight-editing.md](references/highlight-editing.md).
Use [references/cpu-editor-workflow.md](references/cpu-editor-workflow.md) when
bounded proxies or Jianying desktop review are needed.
