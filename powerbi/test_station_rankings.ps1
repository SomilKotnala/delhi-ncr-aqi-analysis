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
$cmd.CommandText = @"
EVALUATE
TOPN(
    10,
    SUMMARIZE(
        dim_station,
        dim_station[station_name],
        dim_station[city],
        "Valid Station-Days", [Valid Station-Days],
        "Median AQI", [Median AQI]
    ),
    [Median AQI],
    DESC
)
ORDER BY [Median AQI] DESC
"@
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$ds = New-Object System.Data.DataSet
$adapter.Fill($ds) | Out-Null
Write-Host "--- TOP 10 MOST POLLUTED STATIONS ---"
$ds.Tables[0] | Format-Table

$cmd.CommandText = @"
EVALUATE
TOPN(
    10,
    FILTER(
        SUMMARIZE(
            dim_station,
            dim_station[station_name],
            dim_station[city],
            "Valid Station-Days", [Valid Station-Days],
            "Median AQI", [Median AQI]
        ),
        [Valid Station-Days] > 0
    ),
    [Median AQI],
    ASC
)
ORDER BY [Median AQI] ASC
"@
$ds2 = New-Object System.Data.DataSet
$adapter.Fill($ds2) | Out-Null
Write-Host "`n--- TOP 10 CLEANEST STATIONS ---"
$ds2.Tables[0] | Format-Table

$conn.Close()
