# Script to finalize delhi_ncr_aqi_analysis.pbix once Power BI Desktop is closed
$ErrorActionPreference = "Stop"

$source = "D:\delhi-ncr-aqi-analysis\delhi_ncr_aqi_analysis_complete.pbix"
$target = "D:\delhi-ncr-aqi-analysis\delhi_ncr_aqi_analysis.pbix"

if (-not (Test-Path $source)) {
    Write-Error "Source file $source does not exist."
    exit 1
}

# Check if PBIDesktop is running
$pbi = Get-Process PBIDesktop -ErrorAction SilentlyContinue
if ($pbi) {
    Write-Warning "Power BI Desktop is currently open (PIDs: $($pbi.Id -join ', '))."
    Write-Warning "Please close Power BI Desktop first, then re-run this script."
    exit 2
}

# Copy with overwrite
Copy-Item -Path $source -Destination $target -Force
$item = Get-Item $target
Write-Output "SUCCESS: Updated $target ($($item.Length) bytes, LastWrite: $($item.LastWriteTime))"
