Add-Type -AssemblyName WindowsBase

$ms = New-Object System.IO.MemoryStream
$pkg = [System.IO.Packaging.Package]::Open($ms, [System.IO.FileMode]::Create)

$testUris = @(
    '/Report/StaticResources/RegisteredResources/theme_navy_environmental.json',
    '/Report/StaticResources/RegisteredResources/Delhi-NCR Environmental Dark Navy',
    '/Report/StaticResources/RegisteredResources/Delhi-NCR Environmental Dark Navy.json',
    '/Report/StaticResources/SharedResources/BaseThemes/Fluent2-CY26SU10.json',
    'Report/StaticResources/RegisteredResources/theme_navy_environmental.json',
    '/Report/StaticResources/RegisteredResources/Delhi-NCR%20Environmental%20Dark%20Navy',
    '/StaticResources/RegisteredResources/Delhi-NCR Environmental Dark Navy',
    '/StaticResources/RegisteredResources/theme_navy_environmental.json',
    'StaticResources/RegisteredResources/Delhi-NCR Environmental Dark Navy',
    'Delhi-NCR Environmental Dark Navy'
)

foreach ($u in $testUris) {
    try {
        $uri = New-Object System.Uri($u, [System.UriKind]::RelativeOrAbsolute)
        $exists = $pkg.PartExists($uri)
        Write-Host "PartExists SUCCESS: '$u' -> $exists"
    } catch {
        Write-Host "PartExists FAILED: '$u' -> $($_.Exception.Message)"
    }
}

$pkg.Close()
$ms.Dispose()
