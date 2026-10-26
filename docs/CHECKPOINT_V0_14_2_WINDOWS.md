# Hoop Roulette v0.14.2 — Windows portable packaging

Replaces the blocked v0.14.1 single-file Windows executable with a portable folder bundle. Extract all files and double-click the EXE alongside `_internal`. No console or Python installation is required. Existing gameplay, data, no-scroll layout, score history and preferences are unchanged. The Apple Silicon Mac release remains v0.14.1.

Uses PyInstaller 6.22.3 in onedir mode with UPX disabled. A Microsoft Defender custom scan runs on the Windows runner before native app tests and package upload. The scan records engine/signature versions, explicit no-threats output and package file hashes, and fails closed on unavailable scanning, detection or changed files. Native checks cover two full games, all fourteen categories, initial/minimum layout, score history, preferences and shutdown.

Local validation: 146 Python tests and frontend checks pass. The Windows CI build passed: Defender explicitly reported no threats across 213 files; native GUI checks passed, including two complete games. Defender engine 1.1.26090.9, signatures 1.461.140.0 dated 2026-10-21. The scan ran on 2026-10-26. Reports are preserved in analysis/desktop_v0_14_2_*. A clean Defender result is a single-engine finding; Chrome Safe Browsing acceptance and code-signing reputation are separate and cannot be guaranteed. The package remains unsigned. The previous block is not claimed to be a confirmed false positive.

## Download

[Windows portable app](https://github.com/andyb33/Hoop-Roulette/actions/runs/40323120570/artifacts/12649628421) — fully extract, then double-click HoopRoulette-v0.14.2-Alpha.exe. Keep `_internal` beside it.

Source commit: b911ca21f02a3dd2e5414772a9830402a907efb0. The previous Windows v0.14.1 single-file package was blocked by Chrome; use this package for the next download test. The original detection is still unresolved.
