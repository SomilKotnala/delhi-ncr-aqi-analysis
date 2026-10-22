# Power BI Desktop Live Tabular Engine DAX Query Runner
# Queries local msmdsrv instance via Microsoft.PowerBI.AdomdClient.dll
param (
    [string]$ServerPort = ""
)

$ErrorActionPreference = "Stop"

# 1. Find and load Microsoft.PowerBI.AdomdClient.dll
$adomdDll = $null
$msProc = Get-Process msmdsrv -ErrorAction SilentlyContinue | Where-Object { $_.Path } | Select-Object -First 1
if ($msProc -and $msProc.Path) {
    $binDir = Split-Path $msProc.Path
    $adomdDll = Join-Path $binDir "Microsoft.PowerBI.AdomdClient.dll"
}
if (-not $adomdDll -or -not (Test-Path $adomdDll)) {
    $adomdDll = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.883.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.AdomdClient.dll"
}
if (-not (Test-Path $adomdDll)) {
    Write-Error "Microsoft.PowerBI.AdomdClient.dll not found."
    exit 1
}

[System.Reflection.Assembly]::LoadFrom($adomdDll) | Out-Null

# 2. Auto-detect msmdsrv port if not provided
if (-not $ServerPort) {
    $msProcesses = Get-Process msmdsrv -ErrorAction SilentlyContinue
    if (-not $msProcesses) {
        Write-Error "No running msmdsrv process found."
        exit 1
    }
    foreach ($proc in $msProcesses) {
        $conns = Get-NetTCPConnection -OwningProcess $proc.Id -State Listen -ErrorAction SilentlyContinue
        foreach ($c in $conns) {
            $candidatePort = $c.LocalPort
            try {
                $testConnStr = "Provider=MSOLAP;Data Source=localhost:$candidatePort;Initial Catalog=;"
                $testConn = New-Object Microsoft.PowerBI.AdomdClient.AdomdConnection($testConnStr)
                $testConn.Open()
                if ($testConn.Databases.Count -gt 0) {
                    $dbName = $testConn.Databases[0].Name
                    $testCmd = $testConn.CreateCommand()
                    $testCmd.CommandText = "EVALUATE ROW(`"Test`", [Total Scheduled Station-Days])"
                    $null = $testCmd.ExecuteScalar()
                    $ServerPort = $candidatePort
                    $testConn.Close()
                    break
                }
                $testConn.Close()
            } catch {
                # Not the right port, try next
            }
        }
        if ($ServerPort) { break }
    }
    if (-not $ServerPort) {
        $firstConn = Get-NetTCPConnection -OwningProcess $msProcesses[0].Id -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($firstConn) {
            $ServerPort = $firstConn.LocalPort
        } else {
            Write-Error "No listening TCP port found for any msmdsrv process."
            exit 1
        }
    }
}

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
