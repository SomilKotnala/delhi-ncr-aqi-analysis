# Power BI Desktop Live Tabular Engine DAX Query Runner
# Queries local msmdsrv instance via Microsoft.PowerBI.AdomdClient.dll
param (
    [string]$ServerPort = ""
)

$ErrorActionPreference = "Stop"

# Auto-detect msmdsrv port if not provided
if (-not $ServerPort) {
    $msmd = Get-Process msmdsrv -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $msmd) {
        Write-Error "No running msmdsrv process found."
        exit 1
    }
    $conn = Get-NetTCPConnection -OwningProcess $msmd.Id -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $conn) {
        Write-Error "No listening TCP port found for msmdsrv process $($msmd.Id)."
        exit 1
    }
    $ServerPort = $conn.LocalPort
}

# Find Microsoft.PowerBI.AdomdClient.dll from running msmdsrv path or default
$binDir = Split-Path (Get-Process msmdsrv -ErrorAction SilentlyContinue | Select-Object -First 1).Path
$adomdDll = Join-Path $binDir "Microsoft.PowerBI.AdomdClient.dll"
if (-not $adomdDll -or -not (Test-Path $adomdDll)) {
    $adomdDll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.883.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.AdomdClient.dll"
}
if (-not (Test-Path $adomdDll)) {
    Write-Error "Microsoft.PowerBI.AdomdClient.dll not found."
    exit 1
}

[System.Reflection.Assembly]::LoadFrom($adomdDll) | Out-Null

# Connect to discover active catalog
$initConnStr = "Data Source=localhost:$ServerPort;"
$initConn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection($initConnStr)
$initConn.Open()
$catalogs = $initConn.GetSchemaDataSet("DBSCHEMA_CATALOGS", $null)
if ($catalogs.Tables[0].Rows.Count -eq 0) {
    Write-Error "No catalogs found on msmdsrv."
    $initConn.Close()
    exit 1
}
$catalogName = $catalogs.Tables[0].Rows[0]["CATALOG_NAME"]
$initConn.Close()

# Connect to specific catalog
$connStr = "Data Source=localhost:$ServerPort;Catalog=$catalogName;"
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection($connStr)
$conn.Open()

$dax = @"
EVALUATE
ROW(
    "Total Scheduled Station-Days", [Total Scheduled Station-Days],
    "Valid Station-Days", [Valid Station-Days],
    "Data Completeness %", [Data Completeness %],
    "Median AQI", [Median AQI],
    "Mean AQI", [Mean AQI],
    "AQI IQR", [AQI IQR],
    "Severe AQI Days Count", [Severe AQI Days Count],
    "Severe AQI Days %", [Severe AQI Days %],
    "Sensor Capped Days Count", [Sensor Capped Days Count],
    "Sensor Capped Days %", [Sensor Capped Days %],
    "Winter Median AQI", [Winter Median AQI],
    "Non-Winter Median AQI", [Non-Winter Median AQI],
    "Winter Elevation Absolute", [Winter Elevation Absolute],
    "Winter Elevation Ratio", [Winter Elevation Ratio],
    "Diwali Matched Station-Years", [Diwali Matched Station-Years],
    "Diwali Pooled Mean Surge", [Diwali Pooled Mean Surge],
    "Diwali Pooled Median Surge", [Diwali Pooled Median Surge],
    "Diwali Elevated Station-Years Count", [Diwali Elevated Station-Years Count],
    "Diwali Station-Years Elevated %", [Diwali Station-Years Elevated %],
    "October Diwali Pooled Mean Surge", [October Diwali Pooled Mean Surge],
    "November Diwali Pooled Mean Surge", [November Diwali Pooled Mean Surge]
)
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $dax
$adapter = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdDataAdapter($cmd)
$ds = New-Object System.Data.DataSet
$adapter.Fill($ds) | Out-Null

$results = [ordered]@{}
foreach ($col in $ds.Tables[0].Columns) {
    $cleanName = $col.ColumnName.TrimStart('[').TrimEnd(']')
    $results[$cleanName] = $ds.Tables[0].Rows[0][$col]
}
$conn.Close()

$results | ConvertTo-Json
