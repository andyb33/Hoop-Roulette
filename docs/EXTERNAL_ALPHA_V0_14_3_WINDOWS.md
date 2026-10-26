# Hoop Roulette v0.14.3 — Windows installer

Extract the download ZIP and run **HoopRoulette-v0.14.3-Setup.exe**. Install for your current Windows account, then open **Hoop Roulette** from the Start menu. No administrator account, CMD or Python installation is required. Uninstall through Windows Installed apps.

The installer places the complete app in `%LOCALAPPDATA%\Programs\Hoop Roulette`. Existing scores and settings remain in `%LOCALAPPDATA%\Hoopreel`; uninstalling does not deliberately remove that save folder. All game data is bundled; gameplay works offline. Microsoft Edge WebView2 Runtime remains required.

This replaces the portable ZIP affected by Windows Internet-zone blocking of bundled .NET DLLs. The installer is tested with an Internet download mark and a Korean-character installation path, without changing global .NET or Windows security settings. CI scans both installer and payload with Microsoft Defender and runs full native gameplay checks on the installed app before upload.

The installer is unsigned, so browser or Windows reputation warnings may still occur; acceptance is not guaranteed. No security protections should be disabled. Apple Silicon Mac remains v0.14.1. Game rules, data and layout are unchanged.
