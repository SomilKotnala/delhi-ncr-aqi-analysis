$adomd = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.883.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.AdomdClient.dll"
[System.Reflection.Assembly]::LoadFrom($adomd) | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:60043;")
$conn.Open()
$ds = $conn.GetSchemaDataSet("DBSCHEMA_CATALOGS", $null)
$ds.Tables[0] | Format-Table CATALOG_NAME, DATE_MODIFIED
$conn.Close()
