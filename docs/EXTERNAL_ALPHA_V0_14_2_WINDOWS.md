# Hoop Roulette v0.14.2 — Windows portable app

Download the Windows Portable ZIP and choose **Extract all**. Open the extracted folder and double-click **HoopRoulette-v0.14.2-Alpha.exe**. Keep the `_internal` folder beside the EXE: moving just the EXE will break the app. You may create a shortcut to the EXE.

No CMD, Python installation or browser tab is required. All data is bundled and gameplay works offline. Microsoft Edge WebView2 Runtime is required, normally already installed on modern Windows.

This changes packaging only: the game, approved no-scroll layout, rules and data match v0.14.1. Existing scores and Instant spins remain in `%LOCALAPPDATA%\Hoopreel\preferences.json`; logs retain the existing Documents folder. Mac users should continue using the Apple Silicon v0.14.1 app.

The Windows build uses a folder bundle instead of a self-extracting single executable, with UPX disabled. CI attempts a Microsoft Defender custom scan and records its engine/signature information and result. A build is uploaded only if the scan and native GUI checks pass. This is a single-engine check, not a guarantee or a Chrome Safe Browsing verdict. The app is unsigned; browser or Windows warnings may remain. Do not disable security protection to run it.
