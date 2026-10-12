# GOAT Spins — v0.6 implementation

Implemented GDD v1.5 on 2026-10-12. The normal pool remains the three verified
modern seasons; expanding the normal pool to 1973–74 onward is a later task.

## Engine

Browser games load both verified GOAT pools. Each first spin or fully unlocked
reroll draws one uniform integer in [0, 1295]; zero triggers a GOAT spin. Choose
Award/Prehistoric equally, then choose uniformly among entries in that pool.
Kept rerolls never check. No Keeps are legal on a GOAT result. Rejected actions
do not consume spins. A released GOAT result gets a fresh check and can return
the same GOAT entry, another jackpot or a normal result. Normal-to-normal
rerolls retain the v1.4 change rule. Three spins per turn and scoring remain.

Actual NBA player IDs stay stable; pool-prefixed identities and entry IDs are
serialized into logs. Missing defensive stats display N/A with an explicit
Sacrifice for 0 action. Historically unavailable awards differ from non-selection;
cumulative First/Second→lower-tier scoring remains available in older seasons.

Existing simulation/CLI callers opt into GOAT pools by passing them to GameState;
their default normal-only behavior preserves the published baseline comparisons.

## Interface

Gold/amber marquee for Award Jackpot; deep purple with blue accents for
Prehistoric Jackpot. Jackpot reels take 1.1/1.5/2 seconds, announce an incoming
legend, then reveal the jackpot type with a short confetti/light response. The
colour persists on the result card. Keep controls are unavailable. Reroll wording
explicitly releases the jackpot. Reduced motion skips cycling and celebration.
No sound in this version.

## Development and evidence

`python scripts/run_web.py --dev-jackpots` enables local preview buttons. The
server rejects forced results otherwise and disallows the flag in packaged or
non-loopback launches. Development games are never saved to playtest logs.
Normal v0.6 games use separate Batch 5 files with pool-aware events and GOAT counts.

65 Python tests pass. JavaScript syntax and live local HTTP routes were checked,
including both forced types, N/A serialization and normal-mode rejection. Local
visual browser QA remains pending: the Chromium download failed in this environment.
Windows/Apple Silicon/Intel packaging workflows bundle both GOAT datasets and
check that the packaged API enables the feature at startup.

## Remaining visual review

Try both previews on desktop and phone-sized screens, including reduced motion.
Check text wrapping, the reveal timing, N/A sacrifice clarity and Keep availability.
