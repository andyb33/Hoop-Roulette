param([Parameter(Mandatory=$true)][string]$PackagePath)
$ErrorActionPreference = 'Stop'
$target = (Resolve-Path $PackagePath).Path
$report = [ordered]@{ target = $target; status = 'not_completed'; scanned_at_utc = [DateTime]::UtcNow.ToString('o') }
try {
    $status = Get-MpComputerStatus
    $report.engine_version = $status.AMEngineVersion
    $report.signature_version = $status.AntivirusSignatureVersion
    $report.signature_updated = $status.AntivirusSignatureLastUpdated.ToString('o')
    if (-not $status.AMServiceEnabled -or -not $status.AntivirusEnabled) { throw 'Microsoft Defender is unavailable or disabled on this runner' }
    $scanner = Get-ChildItem "$env:ProgramData/Microsoft/Windows Defender/Platform/*/MpCmdRun.exe" | Sort-Object FullName -Descending | Select-Object -First 1
    if (-not $scanner) { $scanner = Get-Item "$env:ProgramFiles/Windows Defender/MpCmdRun.exe" }
    $before = @(Get-ChildItem $target -Recurse -File | ForEach-Object { @{ path = $_.FullName; hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash } })
    $output = & $scanner.FullName -Scan -ScanType 3 -File $target -DisableRemediation 2>&1
    $scanExit = $LASTEXITCODE
    $output | Out-File windows-scan.txt -Encoding utf8
    $report.exit_code = $scanExit
    $report.files = $before
    if ($scanExit -ne 0) { throw "Defender scan failed or detected a threat: exit $scanExit" }
    if (($output -join "`n") -notmatch 'found no threats') { throw 'Defender did not explicitly report no threats; inspect scan output' }
    foreach ($file in $before) {
        if (-not (Test-Path $file.path) -or (Get-FileHash $file.path -Algorithm SHA256).Hash -ne $file.hash) { throw "Package changed during scan: $($file.path)" }
    }
    $report.status = 'no_threats_detected'
} catch {
    $report.error = $_.Exception.Message
    throw
} finally {
    $report | ConvertTo-Json -Depth 6 | Set-Content windows-scan.json -Encoding utf8
}
