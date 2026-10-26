# Hoopreel v0.13.0 — standalone desktop alpha

Fully extract the download. Windows: double-click `Hoopreel-v0.13.0-Alpha.exe`. Mac: extract the inner ZIP and double-click `Hoopreel-v0.13.0-Alpha.app`.

Hoopreel opens in its own app window. No CMD window, browser tab, Python installation, account or public website is needed. All 53 seasons and both jackpot pools are bundled; gameplay works offline. Close the app window to stop the game. Closing ends the current unfinished game.

Windows requires Microsoft Edge WebView2 Runtime (normally present on modern Windows). If the app reports that it is missing, install the official Microsoft runtime once, then open Hoopreel again. This is a system rendering component; the app does not open the Edge browser.

The Mac build supports Apple Silicon (M1 or later), not Intel. This alpha is not Developer ID signed or notarized; macOS may require approval through Privacy & Security.

## Testing

Play through complete games and report issues with spins, Keeps, score selection, results dismissal, Instant spins and score history. The pool includes 13,442 entries from 1973–74 through 2025–26. Eligibility and scoring are unchanged. New games use Batch 28.

Completed scores, personal best and Instant spins are saved on this device independently of the local connection port:

- Windows: `%LOCALAPPDATA%\Hoopreel\preferences.json`
- Mac: `~/Library/Application Support/Hoopreel/preferences.json`

Earlier browser-version scores are not automatically imported. Test logs remain in Documents/Hoopreel/playtest_logs. Startup errors are recorded in the app-data directory as `launcher_error.txt`, with request diagnostics in `desktop.log`.

Desktop testing is the current priority. A public web version will be prepared after tester feedback.
