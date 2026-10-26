# Hoop Roulette v0.14.1 — rebrand

The game header, window title, launcher messages, package filenames, build workflows and current brand documentation now use Hoop Roulette. The orange/navy/cream palette, original basketball/reel icon and Spin. Keep. Score. tagline stay in place. The longer wordmark uses a smaller, non-wrapping header treatment.

Scoring, data, layout and QOL controls are unchanged. Existing native and browser score history/preferences keep the same storage identifiers; no migration or reset is required. New games use Batch 30.

Local verification: 146 Python tests and frontend checks pass. Windows and Apple Silicon Mac packages run native GUI gameplay, layout, storage and shutdown checks during CI. Both packages passed native-window checks, including two full games per platform, all fourteen categories, long-name/header geometry, score history, preferences and shutdown. The Mac screenshot was visually inspected; the new wordmark fits cleanly.

Trademark clearance/registration is pending. See BRAND_AND_RIGHTS.md. The repository is now andyb33/Hoop-Roulette; old GitHub repository links redirect to the new address.

## Downloads

- [Windows standalone app](https://github.com/andyb33/Hoop-Roulette/actions/runs/40319162811/artifacts/12648472091)
- [Apple Silicon Mac standalone app](https://github.com/andyb33/Hoop-Roulette/actions/runs/40319162889/artifacts/12648691394)

Fully extract before opening. Mac includes an inner ZIP and supports M1 or later. Build source: `87370560939fe5a873315bc45c04b2f40f2d2bbe`. QA metadata is preserved in `analysis/desktop_v0_14_1_builds.json`; the Mac native report is preserved alongside it.
