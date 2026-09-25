# Use cases and limitations

[简体中文](use-cases.zh-CN.md) · [User guide](usage.en.md)

## Good fits

- **Fixed-camera practice and half-court games:** a stationary hoop and a visible ball allow CPU candidate detection followed by brief visual checks.
- **Manual editing of long recordings:** original-source timecodes and an SRT helper track reduce repeated searching on the editing timeline.
- **Computers without a dedicated GPU:** baseline detection uses OpenCV/NumPy; the exporter uses the Python standard library. CUDA is not needed.
- **NAS footage:** read mounted file paths without uploading footage or transcoding the whole recording first.
- **Previously reviewed data:** reuse event JSON to regenerate tables or SRT files with different marker lengths.

## Additional handling required

| Condition | Recommended handling |
| --- | --- |
| Panning, zooming or camera changes | Separate stable sections and revalidate ROI; the detector CLI does not automatically segment footage |
| Multiple hoops | Analyze each hoop/section separately and deduplicate; each detector run accepts one ROI |
| Tiny, blurred or occluded ball | Increase visual review; keep unresolvable attempts pending |
| HDR, unusual codecs or rotation problems | Verify decoding/display first; preserve source timing and use a compatible editor if needed |
| An already trimmed or retimed editor timeline | Start from the original timeline or establish an explicit time mapping |

## What is not guaranteed

- No trained model weights or production-grade multi-object ball identity tracker are included.
- The baseline does not guarantee complete recall. Sparse screenshots are navigation aids, not evidence that no baskets were missed.
- A ball near the hoop, rim contact or net movement alone does not prove a make.
- Confidence is a heuristic score, not a calibrated probability.
- This release has no full-match precision/recall benchmark or fixed throughput promise.
- SRT is a helper subtitle track, not native editor markers or a complete editor project.

## Speed and accuracy

This release avoids routine proxy encoding, per-event video exports and full shooting-action checks. Full-source decoding, NAS reads and candidate review still take time. Default detection retains every frame rather than risking missed brief crossings through aggressive subsampling. Reuse completed scans and expand only ambiguous review windows.

## Data handling

Processing scripts run locally and do not require a cloud service. Ensure you have permission to process and share your footage. Repository examples are synthetic; do not commit real recordings, NAS addresses, model credentials or machine-specific configuration.
