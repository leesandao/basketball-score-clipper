# User guide

[简体中文](usage.zh-CN.md) · [Home](../README.en.md)

## 1. Installation and runtime

Clone the repository and create a virtual environment as shown in the README. On macOS, install FFmpeg with `brew install ffmpeg`; on Ubuntu/Debian use `sudo apt-get install ffmpeg`. Both `ffmpeg` and `ffprobe` must be on PATH.

From the skill root with the virtual environment activated:

```bash
python scripts/preflight.py --json --require-detection
```

Exporting an existing event JSON requires neither OpenCV nor FFmpeg. Preflight checks the media-processing environment; it is not a prerequisite for the standalone table exporter.

To let subsequent sessions find the virtual environment, create a local configuration in the skill root. Git ignores this machine-specific file:

```bash
python - <<'PY'
import json, shutil, sys
from pathlib import Path
ffmpeg = shutil.which('ffmpeg')
if not ffmpeg:
    raise SystemExit('Install FFmpeg and add it to PATH first')
Path('runtime.json').write_text(json.dumps({
    'python': sys.executable,
    'bin_dir': str(Path(ffmpeg).parent)
}, indent=2) + '\n')
PY
```

## 2. Prepare the source

- Use a local file or an already mounted NAS path, such as `/path/to/game.mp4`.
- Write outputs into a separate directory and never use the source as an output.
- Times start at the beginning of video playback, not the recording date or wall-clock time.
- Inspect duration, rotation and frame rate. Check whether camera position or zoom changes.

```bash
ffprobe -v error -show_format -show_streams -of json /path/to/game.mp4
```

## 3. Invoke the skill

```text
Use $basketball-score-clipper to analyze /path/to/game.mp4.
Locate the instant the ball enters the hoop on the original playback timeline.
Output a timestamp table and SRT subtitle location markers for Jianying.
List uncertain candidates separately. Write to /path/to/output and do not render video.
```

The agent inspects representative frames, determines the hoop ROI, runs detection and reviews consecutive frames near candidates. A moving camera requires a new ROI per stable section or manual review. The default workflow does not launch the editor, generate proxies or render clips.

## 4. Find candidates from the command line

The following ROI is only a syntax example. Replace it with `x,y,width,height` measured from your own video:

```bash
python scripts/detect_fixed_camera.py \
  --input /path/to/game.mp4 \
  --hoop-roi 300,200,80,30 \
  --output /path/to/output/candidates.json --progress
```

Use displayed-frame coordinates after rotation. Keep the default `--frame-step 1` to avoid skipping brief crossings. Processing a hoop crop does not eliminate video decoding or NAS read costs.

All results are `made_candidate`. The detector does not confirm makes. A person or a vision-capable agent must review them; save the updated data separately as `reviewed-events.json`.

## 5. Review and record entry times

1. Inspect consecutive frames before and after the candidate. Confirm downward entry through the rim and continuation through the net.
2. Record the original source time of the first visible entry frame in `basket_entry_time`.
3. Use `entry_time_basis: observed_frame` when directly observed. Use `estimated` with an uncertainty interval in the notes otherwise.
4. Confirmed makes use `result: made` and `review.status: accepted`. False positives use `miss` or `rejected`; ambiguous events remain pending.
5. Keep the original `confidence` and `score_time`. The latter is a later confirmation timestamp and may differ from the entry instant.

See the [synthetic example](../examples/reviewed-events.json) and [event schema](../references/event-schema.md).

## 6. Export the table and SRT

The 120-second duration below is illustrative. Use the actual FFprobe duration for your own source:

```bash
python scripts/export_timestamps.py \
  --events /path/to/output/reviewed-events.json \
  --output /path/to/output/basket-timestamps.md \
  --srt /path/to/output/basket-markers.srt \
  --duration 120 --include-pending
```

- Markdown includes confirmed makes by default. `--include-pending` appends a separate pending table.
- SRT always contains confirmed makes only and requires `basket_entry_time`.
- For multi-source JSON, select the exact source string with `--source`; export a separate SRT for each video.
- `--marker-duration` defaults to one second; ends are clamped to the next marker or video duration.
- Existing outputs are refused. Choose new filenames. No confirmed makes produces an empty SRT; there is nothing to import.
- Millisecond formatting does not imply millisecond detection accuracy. Source frame timing and visual evidence determine precision.
- Output labels currently use Chinese: `进球` means basket, `估算` means estimated, and `待复核` means pending review.

## 7. Locate events in Jianying

1. Place the corresponding original at timeline zero at its original speed, before trimming.
2. Open **字幕 → 新建字幕 → 导入本地字幕** and select the SRT.
3. Keep the playhead at zero and click the add button at the lower-right of the subtitle asset to add it to a helper track.
4. Compare the first marker with the table. Each block's left edge is the entry time used for manual navigation.
5. Hide or remove the helper subtitle track before rendering the edited video.

These are subtitle blocks, not native flag markers. Trimmed, concatenated or retimed footage requires a time mapping first. Do not write undocumented editor draft JSON. Jianying 11.4.2 macOS import and placement were tested; CapCut UI paths may differ.

## 8. Optional clipping and troubleshooting

Use the [clipping workflow](../references/clipping-workflow.md) only when video output is explicitly requested. HDR sources are not silently converted to SDR; tone-mapped review proxies require FFmpeg with `zscale` and `tonemap`, or a verified editor workflow.

| Problem | Action |
| --- | --- |
| Skill not discovered | Invoke in a new turn or provide its absolute `SKILL.md` path |
| Missing dependencies | Activate the environment and check PATH and `runtime.json` |
| Missing or excessive candidates | Check rotated ROI, ball size, lighting and camera movement; confidence is not a substitute for review |
| Legacy events cannot export SRT | Add entry times; do not copy later confirmation times blindly |
| Slow NAS reads | Check mount/network and reuse completed scans; faster-than-real-time performance is not promised |
| Time exceeds duration | Check the source, proxy offset and supplied `--duration` |

## Migrating from v0.1.0

The default deliverable changes from clips to a table and SRT; the skill name stays the same. Legacy JSON can still display confirmation times, but needs entry times for SRT export. Clipping scripts remain available on explicit request. Preserve local edits and machine-specific `runtime.json` when updating.
