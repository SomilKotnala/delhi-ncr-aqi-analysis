Add-Type -AssemblyName WindowsBase

$reportRoot = "D:\delhi-ncr-aqi-analysis\delhi_ncr_aqi_analysis_native.Report"
$files = Get-ChildItem -Path $reportRoot -Recurse -File

Write-Host "Total files found in native Report folder: $($files.Count)"

$ms = New-Object System.IO.MemoryStream
$pkg = [System.IO.Packaging.Package]::Open($ms, [System.IO.FileMode]::Create)

$failedCount = 0
$successCount = 0

foreach ($f in $files) {
    $rel = $f.FullName.Substring($reportRoot.Length).Replace("\", "/")
    $partUriString = "/Report$rel"
    
    try {
        $uri = New-Object System.Uri($partUriString, [System.UriKind]::RelativeOrAbsolute)
        $exists = $pkg.PartExists($uri)
        if (-not $exists) {
            $part = $pkg.CreatePart($uri, "application/json", [System.IO.Packaging.CompressionOption]::Normal)
        }
        $successCount++
    } catch {
        Write-Host "FAILED: $partUriString -> $($_.Exception.Message)" -ForegroundColor Red
        $failedCount++
    }
}

$pkg.Close()
$ms.Dispose()

Write-Host "`nResult: $successCount succeeded, $failedCount failed."
