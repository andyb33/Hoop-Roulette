# v0.13.0 — standalone desktop checkpoint

Windows and Apple Silicon Mac now use a pywebview app window with the existing game and complete data bundled. Windows packaging uses `--windowed`; no external browser is launched. The private loopback game service exists only while the app runs and shuts down after the native window closes. Public web deployment is deferred until desktop testing is satisfactory.

Desktop preference and score history are stored atomically in a dedicated app-data file, avoiding the changing-origin issue of ephemeral local ports. The browser entry point remains available for development and future web deployment; its localStorage behavior is unchanged. In-progress games are not restored after closing.

All QOL controls from v0.12.1 are included. Data and scoring remain unchanged: 53 seasons, 13,442 entries, 1,433 team-seasons, plus existing jackpot pools. New games use Batch 28.

The build workflows now test the actual native window: loading the complete pool, restoring native preferences, spinning, clearing Keeps, confirming the unfinished-game warning, scoring and saving settings. They also require the process to exit and its loopback server thread to stop. This is automated GUI behavior testing, not a human visual playtest.

Both packages passed 146 Python tests, frontend checks and the actual native-window gameplay/storage/shutdown test. The test confirmed all 53 seasons / 13,442 entries and that the local service stops on exit. Built from `d504c20d629093f337787db48bc80da49d1532b8`. Job steps, artifact digests and native QA report artifacts are recorded in `analysis/desktop_v0_13_0_builds.json`.

## Downloads

- [Windows standalone executable](https://github.com/andyb33/Hoopreel/actions/runs/40261242464/artifacts/12624628389)
- [Mac standalone app — Apple Silicon](https://github.com/andyb33/Hoopreel/actions/runs/40261242450/artifacts/12624633396)

Fully extract the archive first. The Mac artifact contains an inner ZIP. GitHub sign-in may be required. Human visual playtesting is still needed.

Earlier build attempts caught a JavaScript Promise test-handshake issue and a Windows close-event deadlock; both are fixed in the successful builds above. GitHub failure emails for earlier attempts do not describe these successful packages.
