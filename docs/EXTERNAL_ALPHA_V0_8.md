Hoopreel v0.8 — Rotation Pool alpha
================================

Award Jackpot is gold; Prehistoric Jackpot is purple and blue. The normal pool
still covers 2023–24 through 2025–26. GOAT pools contain 149 historical award
entries and 15 prehistoric selections.

Windows: extract the artifact ZIP and open Hoopreel-v0.8-Alpha.exe. Keep its
server window open while playing; close it to stop the game.

Mac: choose the Apple Silicon or Intel artifact for your computer. Extract
the artifact ZIP and the app ZIP inside it, then open Hoopreel-v0.8-Alpha.app.
Quit from the Dock or Activity Monitor to stop it. The app is unsigned and
not notarized; macOS may require approval on the first launch.

No Python installation is needed for packaged builds.

Draft rule
----------
Scoring a player, including for 0, removes every version of that real player
from this game. Passed players can return. New Game resets the draft.

GOAT rules
----------
First spins and rerolls with nothing kept have a 1/1,296 combined GOAT chance.
The two jackpot types have equal probability. Entries within each type are
equally likely. No Keeps are allowed on GOAT results: score or spin again.
Consecutive jackpots, including the same entry, are possible. Each consumes
one of the usual three spins. N/A categories can be sacrificed for 0; actual
First/Second-Team awards still qualify cumulatively for lower categories.

Logs
----
Completed games are saved to Documents/Hoopreel/playtest_logs, or the existing
legacy NBA Roulette playtest_logs directory when present. This release uses
Playtest Batch 8 — v0.8 Rotation Pool, with separate JSONL/CSV files. Old batches
remain intact. The batch records up to 100 completed games; play can continue.

Development preview (source checkout only)
------------------------------------------
python scripts/run_web.py --dev-jackpots

Open http://127.0.0.1:8000. Preview buttons appear below Spin. They consume a
normal spin and release all Keeps. Games in this mode are not saved to playtest
logs. Packaged builds and non-loopback servers reject this flag.

Normal eligibility: 30 team GP / 15 team MPG; 943 entries. Upper Bonus stays 120 → +35.
