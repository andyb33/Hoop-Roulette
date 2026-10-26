$ErrorActionPreference = 'Stop'
$installer = (Resolve-Path 'dist/installer/HoopRoulette-v0.14.3-Setup.exe').Path
# Reproduce an Internet download without clearing or weakening its security policy.
Set-Content -LiteralPath $installer -Stream Zone.Identifier -Value "[ZoneTransfer]`r`nZoneId=3"
$destination = Join-Path $env:RUNNER_TEMP '사용자 테스트\Hoop Roulette'
$report = [ordered]@{ installer_marked_as_download = $true; destination = $destination; success = $false }
try {
    $process = Start-Process -FilePath $installer -ArgumentList @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/SP-', "/DIR=`"$destination`"", '/LOG=installer-test.log') -Wait -PassThru
    if ($process.ExitCode -ne 0) { throw "Installer exited with $($process.ExitCode)" }
    $blocked = @(Get-ChildItem $destination -Recurse -Filter *.dll | ForEach-Object { Get-Item -LiteralPath $_.FullName -Stream Zone.Identifier -ErrorAction SilentlyContinue })
    $report.installed_dlls_with_download_mark = $blocked.Count
    if ($blocked.Count -ne 0) { throw 'Installed DLLs still have Internet download marks' }
    python scripts/check_desktop_build.py (Join-Path $destination 'HoopRoulette.exe')
    if ($LASTEXITCODE -ne 0) { throw 'Installed native GUI test failed' }
    $report.success = $true
} catch {
    $report.error = $_.Exception.Message
    throw
} finally {
    $report | ConvertTo-Json -Depth 4 | Set-Content installer-test.json -Encoding utf8
}
