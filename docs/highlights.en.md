# Highlight editing guide

[简体中文](highlights.zh-CN.md) · [User guide](usage.en.md) · [Home](../README.en.md)

Use this workflow only when video output is explicitly requested. The default
remains a timestamp table and Jianying SRT. Selection, player grouping, music
choice and visual judgment require an agent or human reviewer; the bundled
scripts are not an unattended Top 10 generator. This update documents the
editing and review process.

## Selection order

Confirm makes first, assess spectacle second, then meet requested player coverage
and shot categories. Existing accepted records narrow the search but do not
replace a new review of selected plays. Follow the ball through the opening and
net. A ball falling in front of the net, rim contact, net movement or celebration
alone is not proof. Unresolvable attempts stay out of the montage.

Inspect possession through the final basket to identify the scorer. An assist or
a miss followed by a teammate's put-back is not the initial player's make.
For three-pointers, check both feet at takeoff against the visible line rather
than guessing from apparent distance.

## Defensive pressure and player coverage

Select visible close defense, body contact, pursuit, help defense, contests and
interior rebounding. Do not let several similar distance jump shots displace
drives and physical interior play.

Track temporary player IDs using jersey numbers, clothing and action continuity.
Reserve one verified make per distinguishable player before allocating repeats.
Use clothing labels instead of names when appropriate, and leave uncertain
groups unresolved. Passing, defending or appearing in the background does not
count as a scoring highlight.

Coverage depends on available evidence; report players without an eligible make.
A previously unseen player is different from another play by the same person.
Explain missing footage and resolve the fallback before substituting. Neither a
particular roster size nor a three-pointer quota is a universal rule.

## Picture and editing

Keep the setup, acceleration, gather, release, ball flight and clear aftermath.
Fast drives especially need their starting action. Extract short source windows
and reuse completed scans rather than rescanning or transcoding the full match.

Adapt a requested reference's countdown, pacing and layout. For portrait output
from wide half-court footage, keep both shooter and hoop visible. A synchronized
wide view belongs in the upper pane of a split layout; the enlarged slow-motion
pane below follows the ball-handling attacker through the drive, contest, release
and landing by default. After release, stay with the player rather than chasing
the ball to the hoop. Use a dedicated hoop close-up when explicitly requested.

Follow possession to the receiver or actual put-back scorer, not the passer or a
nearby defender. Leave room for the head, body, hands/ball, relevant footwork and
release, retaining nearby defenders where useful. Manually reviewed position
keyframes with smooth interpolation can move the crop without a GPU. Record crop
positions/size against source time and map them to slow motion to avoid jitter,
sudden jumps or tracking lag. Widen the view or return to the wide shot when
occlusion or motion makes the subject unclear.

Check the actual exported replay at the start, drive, gather, release, landing
and ending, including consecutive frames around fast motion and possession
changes. Verify the subject and complete action remain visible. An enlarged
pane is not independent proof of a make.
Inspect framing, color, text and basket sequences in the actual rendered file.

**Playback position differs from rank.** In a 10-to-1 countdown, the seventh
segment is NO.04; NO.07 is the fourth segment. Resolve correction requests using
an on-screen label or playback time.

## Songs, court audio and beat alignment

Preserve usable court sound when adding background music unless removal is
explicitly requested. Mix the song with bounces, contact, rim sounds and voices.
Music can dip near a basket so court sound remains clear.

When a song is requested, use an actual track with a complete melody and
arrangement rather than substituting generated percussion. Prefer the user's
available chosen music; when choosing yourself, record title, artist, source,
usage permission/license and required attribution. State whether it is an
instrumental or a vocal song.

Verify beat and downbeat phase from the recording, not BPM alone. Align countdown
cards, cuts, replay transitions and suitable basket moments with audible beats.
Adjust lead-in and aftermath first; never cut off the action or arbitrarily
speed up an ordinary play to force alignment. Recheck timing after replacements.

Keep a court-audio master for future soundtrack changes. Listen to actual live
action, replay, transitions and ending. Meter readings do not replace listening;
disclose when a listening check is unavailable.

## Correcting a wrong basket

Exclude disputed footage, preserve the prior review and evidence, and update the
authoritative event JSON with the current status and correction reason. Refresh
affected selection JSON, table, SRT and video files so stale acceptances cannot
reintroduce a miss. Review the replacement in the source and rendered file, then
check subsequent beat alignment, labels and audio. Fixing a few events does not
revalidate every historical record.

## Example request

This optional style does not change the timestamp-only default:

```text
Use $basketball-score-clipper to make a Top 10 from /path/to/game.mp4.
Confirm each made basket first, then select 3 exciting three-pointers and
7 contested finishes. Aim for at least one make per player and preserve
complete actions. Keep court audio, add a fully arranged song and edit to
its actual beats. Make enlarged slow motion follow the ball-handling attacker,
with a synchronized wide view above. Include original-source basket times. Report coverage
gaps and exclude uncertain attempts.
```

See the [editing reference](../references/highlight-editing.md) for operational
details. Local rendering does not authorize public uploads. Git updates contain
the skill, code and documentation, not private media or music.
