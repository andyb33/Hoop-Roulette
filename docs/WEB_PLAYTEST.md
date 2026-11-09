# Hoop Roulette — small web playtest

Status: owner confirmed desktop and phone work after the deployed dialog fix on 2026-11-09. Device/browser versions were not supplied.

Game: https://hoop-roulette-web.bouncykiwi13.chatgpt.site

## Access
Private alpha for 3–5 invited testers. The site currently allows only the owner. Add testers as external viewers using their email addresses; do not make the site public. Inviting a viewer may send an invitation email. No testers have been invited yet.

## Tester instructions
Play two complete games in the same browser if possible. Try learning the first game without coaching. Spin, keep slots, and fill the 14-category scorecard. Try Scores, canceling New Game, and refreshing after scoring a turn. After finishing, check that the game appears in Scores.

Scores and progress are stored in this browser on this device. Use a normal browser tab; clearing browser data can remove them. There is no cross-device sync.

Please send back:
1. Was anything confusing? Where did you hesitate?
2. Did anything break? Include device, browser, steps and a screenshot if possible.
3. Did you want to play again? Why or why not?

Optional: Scores → Export playtest logs, then send the downloaded file to Andy manually. Nothing is uploaded automatically.

## Organizer feedback record
Use one row per tester; do not put private email addresses in this public repository.

| Tester alias | Device / browser | Games | Confusion | Bugs / steps | Play again? / reason |
| --- | --- | --- | --- | --- | --- |
| T1 | Pending | | | | |
| T2 | Pending | | | | |
| T3 | Pending | | | | |
| T4 (optional) | Pending | | | | |
| T5 (optional) | Pending | | | | |

Review after 3–5 people: fix blockers first, clarify repeated confusion, then choose feature work from replay feedback. This is exploratory feedback, not a balance study.

## Dialog fix checkpoint
The deployed fix explicitly centers native dialogs in the viewport, bounds them to the visible height, and retains internal scrolling and touch-sized action buttons. Source mirrored in browser/styles.css. Hosted source commit: c37a9bd1946e329c5127cbf760d639595fbabcbc.

Previous browser QA checked desktop Scores dismissal, phone-width Scores/New Game cancellation, and score persistence across refresh. Owner subsequently reported desktop and phone work. No claim of testing every device/browser is made. Rules, data and desktop installers are unchanged.
