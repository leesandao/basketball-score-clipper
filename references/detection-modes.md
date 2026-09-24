# Detection modes

## Fixed-camera baseline

Use only when the hoop is stationary and an orange-ball motion mask is plausible. The bundled baseline combines HSV color, frame difference, contour shape, temporal continuity, and an above-to-below hoop crossing. It intentionally emits candidates rather than confirmed makes.

Provide a tight hoop bounding box in displayed-frame pixels. Recheck the ROI when resolution, rotation, zoom, camera position, or crop changes. A static orange rim is largely suppressed by motion filtering, but clothing, lights, skin tones, and compression artifacts can still create false positives.

Good baseline footage has:

- a tripod or otherwise stable camera;
- one visible hoop;
- the ball at least several pixels across near the hoop;
- limited occlusion at the rim;
- consistent lighting and white balance.

## Detector-backed analysis

Use a trained basketball/hoop detector plus temporal tracking when the baseline assumptions fail. A practical two-pass design is:

1. Run a lower-cost full-video pass to locate the hoop and intervals containing a ball approaching the hoop.
2. Re-run only those intervals at full frame rate and higher resolution, preferably on a crop around the hoop and incoming trajectory.

The tracker should retain low-confidence ball observations, interpolate only short gaps, and reject jumps that violate plausible velocity. Stabilize or redetect the hoop when the camera pans or zooms. Human pose can improve `release_time`, but it is not required for confirming the basket.

For a made shot, prefer multiple independent observations:

- tracked ball above the rim plane;
- tracked ball moving downward through the horizontal hoop corridor;
- tracked ball below the rim shortly afterward;
- consistent identity and velocity across the crossing;
- optional net movement, rim interaction, pose, or audio support.

Emit the standard event contract even when the underlying model has its own output format.

## Evaluation

Split validation data by recording session or source video, not by random adjacent frames. Measure event-level precision and recall in addition to detector mAP. Also measure whether each produced clip contains the gather/release, flight, basket, and a usable ending.

False-positive review should include downward passes near the hoop, airballs, rim bounces, rebounds, orange clothing, heads, and a stationary rim. False-negative review should include occlusion, motion blur, backboard overlap, low light, and small distant balls.
