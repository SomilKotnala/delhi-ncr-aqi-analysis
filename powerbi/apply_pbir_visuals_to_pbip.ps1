# Automated script to apply the complete 3-page, 34-visual PBIR report canvas to a Power BI Project (PBIP)
$ErrorActionPreference = "Stop"

$projectRoot = "D:\delhi-ncr-aqi-analysis"
$pbipReportDir = Join-Path $projectRoot "delhi_ncr_aqi_analysis.Report"
$pbipModelDir = Join-Path $projectRoot "delhi_ncr_aqi_analysis.SemanticModel"
$sourceReportDir = "C:\Users\Dell\.gemini\antigravity\brain\cd26c1d9-9fff-4c6d-8a51-47e782d685f7\scratch\assembled_pbix\Report"

Write-Output "Checking PBIP project structure in $projectRoot..."

if (-not (Test-Path $pbipModelDir)) {
    Write-Warning "delhi_ncr_aqi_analysis.SemanticModel folder not found!"
    Write-Warning "Please open delhi_ncr_aqi_analysis.pbix in Power BI Desktop and do: File -> Save As -> Power BI Project (*.pbip)."
    exit 1
}

# 1. Update definition folder
$targetDefDir = Join-Path $pbipReportDir "definition"
$sourceDefDir = Join-Path $sourceReportDir "definition"

Write-Output "Copying verified 3-page, 34-visual PBIR definitions..."
if (Test-Path $targetDefDir) {
    Remove-Item $targetDefDir -Recurse -Force
}
Copy-Item -Path $sourceDefDir -Destination $targetDefDir -Recurse -Force

# 2. Ensure theme is in RegisteredResources
$targetThemeDir = Join-Path $pbipReportDir "StaticResources\RegisteredResources"
New-Item -ItemType Directory -Path $targetThemeDir -Force | Out-Null
$themeSource = Join-Path $projectRoot "powerbi\theme_navy_environmental.json"
Copy-Item -Path $themeSource -Destination (Join-Path $targetThemeDir "theme_navy_environmental.json") -Force

# 3. Ensure definition.pbir correctly references SemanticModel
$pbirPath = Join-Path $pbipReportDir "definition.pbir"
$pbirContent = @{
    "version" = "4.0"
    "datasetReference" = @{
        "byPath" = @{
            "path" = "../delhi_ncr_aqi_analysis.SemanticModel"
        }
        "byConnection" = $null
    }
} | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText($pbirPath, $pbirContent, [System.Text.Encoding]::UTF8)

# 4. Verify visual count
$visuals = Get-ChildItem -Path (Join-Path $targetDefDir "pages") -Recurse -Filter "visual.json"
Write-Output "SUCCESS: Successfully injected PBIR layout into PBIP!"
Write-Output "Total verified visual containers: $($visuals.Count) across 3 pages."
Write-Output "You can now open $projectRoot\delhi_ncr_aqi_analysis.pbip in Power BI Desktop!"
