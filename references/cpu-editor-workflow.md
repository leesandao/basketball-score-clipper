# CPU / NAS / Jianying workflow

Use this route for local or mounted NAS video when no validated trained detector
is available. Do not require CUDA. The editor provides playback and editing;
it does not establish that a basketball went through the hoop.

## Prepare and locate

1. Resolve the input file and a separate local output folder. Inspect media
   metadata before processing. Leave NAS originals in place. Use short local
   proxies rather than copying an entire long source by default.
2. Run `preflight.py --json`. Read `runtime.json` if installed to find the
   configured Python and FFmpeg binaries. OpenCV/NumPy are optional unless
   using fixed-camera detection.
3. Create a bounded viewing proxy:

   ```bash
   python3 "$SKILL_DIR/scripts/prepare_review.py" \
     --input /absolute/source.mp4 --output-dir /absolute/local/review-001 \
     --start 0 --duration 60
   ```

   The helper produces `review.mp4` and `source-map.json`, refuses existing
   outputs, preserves variable frame timing, and explicitly tone maps HDR to
   SDR only for this viewing derivative when `zscale` and `tonemap` are available.
   Otherwise it reports the missing HDR support. Final clips must come from originals.
4. Inspect continuous footage. Sparse thumbnails are navigation only and cannot
   establish recall or prove a make. For long sources, work in bounded windows
   with at least six seconds of overlap; track reviewed source ranges and
   deduplicate events in overlaps. Expand the window if the gather is offscreen.
5. When the camera is fixed and a representative frame confirms a suitable hoop
   ROI, optionally run `detect_fixed_camera.py`. Use source displayed-frame
   coordinates, not scaled proxy coordinates. Its events remain candidates.
   Moving cameras or small/occluded balls require visual review instead.

## Jianying desktop review

Use the available computer-use tool to inspect the actual installed UI. Open a
new local project for this work; do not modify an unrelated existing draft.
Import the local review proxy. Observe the timeline, scrubbing controls and
keyboard shortcuts before using them; do not guess coordinates or shortcuts.
If desktop permissions are blocked, report that precise blocker and continue
with local frame-sequence review where available. Do not claim editor testing
when only a command-line export succeeded.

Confirm the ball's approach, downward hoop crossing and aftermath using multiple
consecutive frames. Record uncertain events as `made_candidate` / `pending`.
Use `made` / `accepted` only with sufficient visible evidence, and record the
method and observations in `review.notes`. Source seconds equal proxy seconds
plus `source_start` from the mapping file. Store source paths and source times
in event JSON. Keep the original detector confidence after visual review.

## Export and verify

Run `clip_events.py --events ... --output-dir ... --dry-run`, inspect the plan,
then export without `--dry-run`. The script checks actual encoder startup for
`auto` and can fall back to CPU before processing. A source with HDR transfer
metadata is refused for implicit SDR reencoding; use the editor with verified
HDR/color settings for final HDR output. `--encoder copy` is only suitable
when approximate keyframe boundaries are explicitly acceptable.

For a Jianying final export, import the original, apply the recorded source
times and inspect the export settings. Verify the produced file, duration,
audio and visible start, release, crossing and ending. Never write undocumented
draft JSON or report a draft as a rendered video.

For a pilot, report separately: media read, proxy generated, event visually
confirmed, source clip exported, clip visually checked, and editor UI tested.
An arbitrary segment validates media handling but is not a confirmed basket.
Do not process the full match when the user requested only setup and a pilot.

## Tested desktop interaction notes

In Jianying 11.4.2 on macOS, importing media only selects a preview; it does not
necessarily insert it into the timeline. The media context menu option
“根据选中素材新建时间线” successfully creates a populated timeline. The native
file dialog accepts `slash` to open a path field, then setting the absolute path
and Return. Some custom buttons expose accessibility names but do not respond
to an accessibility click; a screenshot-grounded coordinate click may be needed.
Re-observe the actual UI rather than assuming this version's layout persists.
A successful local export may open a publish/share screen; close that screen
unless the user explicitly requests publishing. Local export alone is sufficient.
