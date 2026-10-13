# Verified highlight selection and editing

Read this only for an explicitly requested montage, ranked selection, soundtrack
or revision. The default remains a timestamp table and SRT. This is an assisted
editing workflow, not a bundled automatic Top N or music-composition command.

## Select makes before judging spectacle

- Reuse the source scan and shortlist with contact sheets. Then inspect complete
  action and consecutive rim frames for every selected event. Sparse frames are
  navigation aids; an `accepted` field is not fresh visual evidence.
- Follow downward entry through the opening and continuation through the net.
  A front/side miss may overlap the rim and net in projection. Net flicks, a ball
  below the rim and player reactions cannot establish a make independently.
  Expand the interval/view or leave the event pending when the path is unclear.
- Track possession, release, rim contact and any rebound. Credit the actual
  scorer; distinguish an assist, a missed initial shot and a teammate's put-back.
- Only after confirming makes, judge visible defender proximity, lateral
  containment, body contact, help defense, contested release and action clarity.
  Distance shooting alone does not imply high defensive pressure. Describe what
  the footage shows rather than inventing fouls, scores or game stakes.
- For a requested three-pointer, check both feet at takeoff against the visible
  three-point line. A long shot or a shooter near the edge of the frame is not
  sufficient. Keep uncertain distance labels out of a strict three-point quota.

## Respect the requested selection and cover players

Apply the latest requested size, shot mix, retained plays and player coverage.
For example, `3 three-pointers + 7 contested finishes` is a user profile, not a
universal Top 10 rule. If the user does not specify a mix, use variety and avoid
letting several similar jump shots crowd out drives and interior play.

Maintain a small selection table with stable local player IDs, visible jersey
number/clothing labels, event IDs, source times, shot type and selection reason.
Labels describe the footage; do not infer names. Keep a group `unknown` when
clothing is ambiguous, and verify continuity before merging or splitting groups.
A clothing change does not automatically mean a new player.

When broad coverage is requested, reserve one verified make per distinguishable
player before allocating repeat slots. Recheck the roster after substitutions.
Record coverage as confirmed scoring appearances; appearing in the background,
passing, defending or making a disputed attempt does not satisfy that criterion.
Do not claim complete roster coverage without inspecting the relevant footage.

If the user asks for someone never shown in the current montage and no such
player can be found, explain the limitation and resolve the fallback. A different
play by the same player is not a new player. Do not invent a ninth player, import
an unrelated adjacent-court basket, or silently substitute an already featured
player while claiming that the request was met.

Separate `rank` (the on-screen NO. label) from `play_order` (segment position).
For a 10-to-1 countdown, `play_order = 11 - rank`. Resolve ambiguous phrases such
as “the seventh play” using a visible label or playback time before replacing it.

## Preserve the action and adapt the reference style

Record explicit source bounds after inspecting the gather, change of direction,
release and follow-through. Include enough aftermath to establish the make.
For a fast drive, show the setup and acceleration, not just the final rim frame.
Inspect the actual cut rather than assuming a fixed lead-in is sufficient.

Extract only shortlisted source windows. Read NAS originals in place; avoid a
new full-source scan/transcode for a selection or music-only revision. Keep a
court-audio master so later soundtrack changes can restore the original audio.

Borrow the requested reference's pacing, layout and countdown structure without
assuming its audio or graphics are reusable assets. With wide half-court footage,
a vertical canvas containing the horizontal action can preserve shooter and rim
better than a tight vertical crop. Verify the composition at takeoff and entry.
Use a synchronized hoop inset during replay when it helps; the inset enlarges
evidence and does not itself validate a basket. Follow any requested aspect ratio.

## Choose real music and mix it with court sound

Music is optional and follows the user's request. Preserve usable court sound
when adding background music unless the user explicitly requests its removal.
Retain ball bounces, contact, rim sounds and reactions at intelligible levels.
For a music-only change, remux the verified video where possible.

If the user specifies a song, use their available authorized source. If asked to
choose, select an actual track with a complete arrangement and suitable energy.
Do not substitute generated percussion or a synthetic beat for a requested song
without agreement. Distinguish instrumental music from vocal songs when relevant.
Record title, artist, source, usage permission/license and required credit. Include
attribution in the output when the chosen license requires it. Do not commit
downloaded music or private footage to the public skill repository.

Balance music and court sound together. Listen to representative live action,
replay, transitions and ending; meter readings and successful muxing do not prove
that the mix sounds good. If listening is unavailable, report that limitation
rather than claiming a listening pass. Music may rise during title cards and
replay and dip around salient court sounds. Avoid abrupt gain changes, clipping
and excessive ducking. Slow replay audio with pitch preservation where appropriate.

## Align cuts to the actual song

Establish tempo **and beat/downbeat phase from the recording**. A nominal BPM or
looped generated drum grid is insufficient to claim alignment to the chosen song.
Choose an effective musical section and record its starting offset.

Align title changes, action/replay transitions and selected basket moments with
audible beats when feasible. Adjust lead-in/post-roll or transition length before
changing the action speed. Preserve the gather and flight; do not truncate the
play, reverse footage or accelerate an ordinary make just to hit a beat.

For a source entry `s`, source start `a`, playback speed `v` and montage start `m`,
the mapped entry is `m + (s - a) / v`. Record each segment's source bounds,
montage bounds, speed and mapped entry. Round cuts to the output frame grid and
measure alignment at the achieved timestamps. Quote only the accuracy actually
verified. Recheck synchronization after replacing a clip or changing its length.

## Verify the final file and propagate corrections

Check the actual rendered gather, release, basket and exit for every selected
play, including the scorer and any overlays. Confirm labels, rank/play order,
player quotas, three-point evidence, color/rotation, audio and full-file decoding.
Technical checks supplement visual/listening checks; they do not replace them.

When a user flags a miss, remove it from the selection immediately. Preserve the
old review and evidence, mark the authoritative event rejected/miss or pending
as appropriate, and record the reason and provenance of the correction. Never
reaccept it merely because another copy still contains `accepted`.

Update affected selected-event files, timestamps/SRT and montage outputs. Preserve
older deliverables as clearly superseded versions and identify the new file.
Review the replacement from the original and from the rendered output, then
recheck timing, music and labels affected by its duration. A partial correction
does not mean every other old record was revalidated.

Deliver the video and a concise selection/time table. State substitutions or
unmet coverage constraints plainly. Keep original videos, real match metadata,
NAS addresses, music and local runtime settings out of a public Git update.
