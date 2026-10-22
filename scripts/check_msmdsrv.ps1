[System.Reflection.Assembly]::LoadFrom("C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.883.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.PowerBI.AdomdClient.AdomdConnection("Provider=MSOLAP;Data Source=localhost:55237;Initial Catalog=;")
$conn.Open()
Write-Host "Databases count: $($conn.Databases.Count)"
foreach ($db in $conn.Databases) {
    Write-Host "Database: $($db.Name)"
}
$conn.Close()
