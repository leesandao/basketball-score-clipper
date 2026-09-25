# Event file contract

Use UTF-8 JSON. The root is an object with `version`, optional shared `source`, and an `events` array. Times are seconds on the source video timeline and must be finite, non-negative numbers.

```json
{
  "version": 1,
  "source": "/absolute/path/game.mp4",
  "detector": {
    "name": "fixed-camera-baseline",
    "mode": "candidate-only"
  },
  "events": [
    {
      "id": "score-0001",
      "source": "/absolute/path/game.mp4",
      "result": "made_candidate",
      "confidence": 0.72,
      "candidate_start": 121.2,
      "release_time": null,
      "score_time": 125.2,
      "clip_start": 121.2,
      "clip_end": 126.7,
      "evidence": {
        "above_rim_time": 124.83,
        "below_rim_time": 125.20,
        "downward_crossing": true,
        "hoop_roi": [812, 188, 96, 48]
      },
      "review": {
        "status": "pending",
        "notes": ""
      }
    }
  ]
}
```

## Required event fields

- `id`: unique within the document.
- `result`: one of `made`, `made_candidate`, `miss`, or `rejected`.
- `confidence`: number from 0 through 1.
- `score_time`: time at which the downward basket crossing is confirmed.

`source` may be specified once at the root or per event. A relative path is resolved from `--source-root` when supplied, otherwise from the event file's directory.

## Boundary precedence

The clipping script derives boundaries in this order:

1. Use explicit `clip_start` and `clip_end` when both are present.
2. Start at `release_time - pre_roll` and end at `score_time + post_roll`.
3. Start at `candidate_start` and end at `score_time + post_roll`.
4. Start at `score_time - fallback_lead` and end at `score_time + post_roll`.

All boundaries are clamped to the source duration. An event whose end is not after its start is invalid.

## Review updates

After visual review, change a real make from `made_candidate` to `made` and set `review.status` to `accepted`. For a miss or false positive, set `result` to `rejected` or `miss` and use `review.status: rejected`. Preserve the original evidence and add a short note instead of deleting the event.

## Selection and time provenance

Explicit visual acceptance (`result: made`, `review.status: accepted`) bypasses
the model confidence threshold. Preserve the original confidence. A rejected
review is never selected; a pending make is not automatically accepted.
Candidates must still meet `--min-confidence` even with `--include-candidates`.

All event times refer to the original source timeline. When reviewing a proxy,
read `source-map.json` and add `source_start` to its playback time. Record the
reviewer/method and observations in `review.notes`; never mark an export test
or an unobserved basket as accepted. Explicit bounds must include `score_time`.

## Timestamp-only output

- `basket_entry_time`: optional finite non-negative source time of entry into the
  rim opening. This is distinct from the later `score_time` confirmation.
- `entry_time_basis`: `observed_frame` or `estimated` when entry time is present.
- For an observed frame, choose the first frame showing downward entry; inspect
  subsequent frames to confirm the make. Do not infer precision from formatting.
- `review.notes`: explain occlusion or the uncertainty interval if estimated.

`export_timestamps.py` includes only `made` + `review.status: accepted` by default.
It prefers entry time; older events without it are explicitly labeled as
confirmation timestamps awaiting precise entry localization. Pending events are
optional and exported separately, never counted as confirmed makes.
