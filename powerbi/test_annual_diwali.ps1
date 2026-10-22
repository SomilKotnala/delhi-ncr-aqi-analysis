param([int]$port = 60052)
$adomd = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.883.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.AdomdClient.dll"
[System.Reflection.Assembly]::LoadFrom($adomd) | Out-Null
$c = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;")
$c.Open()
$cat = $c.GetSchemaDataSet("DBSCHEMA_CATALOGS", $null).Tables[0].Rows[0]["CATALOG_NAME"]
$c.Close()

$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;Catalog=$cat;")
$conn.Open()
$cmd = $conn.CreateCommand()
$cmd.CommandText = "EVALUATE SUMMARIZE('fact_diwali_pairs', 'fact_diwali_pairs'[year], `"Annual Mean Surge`", [Diwali Pooled Mean Surge]) ORDER BY 'fact_diwali_pairs'[year]"
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$ds = New-Object System.Data.DataSet
$adapter.Fill($ds) | Out-Null
$ds.Tables[0] | Format-Table
$conn.Close()
