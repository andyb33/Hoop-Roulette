# Hoop Roulette v0.14.3 — Windows installer

The portable v0.14.2 app downloaded successfully but failed on the tester's Windows machine. The first log failed while loading Python.Runtime.dll. After that DLL was unblocked, the next log reached Microsoft.Web.WebView2.Core.dll and explicitly reported .NET Internet-zone assembly blocking (0x80131515). Unblocking/re-extracting the ZIP did not resolve startup for the tester. Do not treat the CI portable launch as sufficient evidence of post-download compatibility.

v0.14.3 replaces the loose-DLL ZIP with an Inno Setup per-user installer. It places the complete app in LocalAppData/Programs/Hoop Roulette, adds a Start-menu shortcut and supports ordinary Windows uninstallation. Scores/settings remain in the existing Hoopreel app-data folder and are not removed by the installer. No global .NET settings, antivirus exclusions, execution-policy changes or automatic unblocking are added.

The build scans the app payload and installer with Microsoft Defender. Regression checks mark the installer as an Internet download, install into a Korean-character path, verify installed DLLs do not retain an Internet-zone mark, then launch the installed app and run native gameplay/layout/storage/shutdown checks. This simulates file-zone propagation, not actual Chrome/SmartScreen download approval. The installer remains unsigned; tester confirmation is still required.

Gameplay, rules, data and UI are unchanged. Apple Silicon Mac remains v0.14.1. All 146 Python tests and frontend checks passed. The installer regression passed: Internet-marked installer, Korean-character path, zero installed DLLs with download marks, two complete native games and successful layout/history/storage/shutdown checks. Defender explicitly reported no threats in payload and installer (engine 1.1.26090.9, signatures 1.461.140.0 dated 2026-10-21; scanned 2026-10-26). Reports are in analysis/desktop_v0_14_3_*.

## Download

[Windows v0.14.3 installer](https://github.com/andyb33/Hoop-Roulette/actions/runs/40325991931/artifacts/12651327181). Extract the ZIP, run HoopRoulette-v0.14.3-Setup.exe, then open Hoop Roulette from the Start menu. Source commit: 6baa84aa750635f2d4b69427e8129e99a9ffb8d9.
