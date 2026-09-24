---
name: basketball-score-clipper
description: Analyze local basketball videos to find made-shot candidates, preserve the complete action from the shooting motion through the basket, and create verified highlight clips. Use for basketball score detection, shot-to-score clipping, batch highlight extraction, or reviewing uncertain made baskets; do not use for unrelated general-purpose video editing.
---

# Basketball Score Clipper

Find made baskets first, then cut complete plays. Do not treat a frame in which the ball is near the hoop as proof of a score.

Resolve this skill directory as `SKILL_DIR` before running bundled scripts. Keep every source video unchanged and write all generated files to a separate output directory.

## Select the operating mode

- **Fixed-camera baseline:** Use when one hoop remains stationary, the ball is visibly orange, and lighting is reasonably stable. Run `scripts/detect_fixed_camera.py` with a verified hoop ROI. Its results are `made_candidate` events and require visual review.
- **Detector-backed analysis:** Use for handheld footage, moving/zooming cameras, crowded games, poor lighting, heavy occlusion, or multiple hoops. Use the project's trained ball/hoop detector and tracker; it must emit the event format in [references/event-schema.md](references/event-schema.md). Never imply that a production detector exists when weights or an inference command are absent.
- **Known-event clipping:** Use when timestamps or an event JSON already exist. Skip detection and validate/cut those events directly.

Read [references/detection-modes.md](references/detection-modes.md) when choosing or implementing a detector. Read [references/event-schema.md](references/event-schema.md) before generating or editing event files.

## Workflow

1. Locate the local source videos and choose an output directory. If the files are still on a phone or inaccessible host, stop and identify the concrete transfer needed.
2. Run preflight:

   ```bash
   python3 "$SKILL_DIR/scripts/preflight.py" --json
   ```

   FFmpeg and FFprobe are required for clipping. The fixed-camera detector additionally needs OpenCV and NumPy. Prefer CUDA for trained-model inference when available; CPU fallback is acceptable. Hardware encoding is an optimization, not a detection requirement.
3. Probe every source before analysis. Respect rotation, frame rate, variable-frame-rate timing, duration, audio streams, and HDR metadata. If `ffmpeg-skill` is installed, use its `probe.py`/`look.py` workflow for probing and visual QA.
4. Detect events:
   - For the fixed-camera baseline, inspect a representative frame and obtain a pixel ROI in `x,y,width,height` form that tightly covers the hoop. Do not guess an ROI without viewing the frame.
   - Run the baseline detector and keep its candidates for review:

     ```bash
     python3 "$SKILL_DIR/scripts/detect_fixed_camera.py" \
       --input /absolute/source.mp4 \
       --hoop-roi x,y,width,height \
       --output /absolute/events.json
     ```

   - For detector-backed analysis, associate the same ball track across the upward approach and downward hoop crossing. Generate one event per attempt, not one event per confirming frame.
5. Validate the event timeline. Strong made-shot evidence normally includes a ball center above the rim followed by a downward crossing through the hoop corridor and a ball center below the rim within a plausible interval. Rim contact, net motion, audio, and pose are supporting evidence only.
6. Apply confidence routing:
   - `confidence >= 0.85`: may be accepted automatically only for a validated detector.
   - `0.55 <= confidence < 0.85`: create review clips and require visual confirmation.
   - `< 0.55`: retain in metadata if useful, but do not include in the final montage.
   - Fixed-camera baseline output is always review-first, regardless of its numeric confidence.
7. Preserve the complete action. Prefer an observed `release_time`; otherwise start from `candidate_start`. When neither exists, default to four seconds before `score_time`. Default end is 1.5 seconds after `score_time`. Keep more context rather than cutting off the gather or release.
8. Cut accepted events with the bundled script:

   ```bash
   python3 "$SKILL_DIR/scripts/clip_events.py" \
     --events /absolute/events.json \
     --output-dir /absolute/clips
   ```

   Add `--include-candidates --min-confidence 0.55` only when intentionally creating review clips. Use `--encoder auto` to prefer NVENC on a compatible RTX host, VideoToolbox on macOS, and `libx264` otherwise. Do not use stream copy when frame-accurate boundaries matter. For HDR sources, use the installed `ffmpeg-skill` HDR-aware cut workflow; the bundled fallback refuses an implicit HDR-to-SDR conversion.
9. Inspect at least the beginning, release/flight, rim crossing, and ending of every accepted clip. Reject clips that begin after the gather/release, end before the score is visually clear, duplicate another event, or show a miss. Use `ffmpeg-skill` to join verified clips when available.
10. Report source files, accepted/rejected/review counts, selected time ranges, encoder used, output locations, and any detector limitations. Never report a candidate as a confirmed make without the required evidence or review.

## Output layout

For repeatable projects, initialize a working layout with:

```bash
python3 "$SKILL_DIR/scripts/init_project.py" --root /absolute/project
```

The layout contains `input/`, `events/`, `clips/`, `review/`, `models/`, and `basketball-score-clipper.json`. Originals belong in `input/`; do not move or overwrite them during analysis.

## Boundaries

- A camera that never captured the shooter cannot provide a true release timestamp; label the start as estimated and use extra pre-roll.
- Generic object detectors often miss a small, motion-blurred basketball. Do not claim robust detection until it has been evaluated on footage from the target camera setup.
- The fixed-camera script is a bootstrapping detector, not a substitute for a trained ball/hoop model in real games.
- Never upload private footage or install models/services unless the user requested that action.
