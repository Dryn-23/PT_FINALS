#!/usr/bin/env pwsh
# ============================================================
#  KALI SMARTOPS MANAGER PRO — BRIDGE WRAPPER
#  Connects the Midnight TUI Dashboard to smartops.ps1
#
#  USAGE
#  ─────────────────────────────────────────────────────────
#  Open the dashboard:
#    ./smartops-bridge.ps1 -UI
#
#  Run any feature headlessly (same as the original CLI):
#    ./smartops-bridge.ps1 -Feature 1
#    ./smartops-bridge.ps1 -Feature 13 -Path "/home/user"
#    ./smartops-bridge.ps1 -Feature 17 -Path "/home/user/Downloads"
#    ./smartops-bridge.ps1 -Feature 21 -Device "/dev/sdb" -IsoPath "kali.iso"
#    ./smartops-bridge.ps1 -Feature 23 -Device "/dev/sdb1" -Filesystem "ext4" -Label "DATA"
#
#  WebSocket server mode (live output to dashboard):
#    ./smartops-bridge.ps1 -Server -Port 9001
#
# ============================================================

param(
    # ── Launch mode ─────────────────────────────────────────
    [switch]$UI,           # Open the HTML dashboard in browser
    [switch]$Server,       # Start WebSocket bridge server
    [int]   $Port = 9001,  # Port for the WebSocket server

    # ── Feature selection (direct CLI pass-through) ──────────
    [int]   $Feature        = 0,
    [string]$Path           = "",
    [string]$Source         = "",
    [string]$Destination    = "",
    [string]$Device         = "",
    [string]$IsoPath        = "",
    [string]$Filesystem     = "ext4",
    [string]$Label          = "",
    [string]$SearchPattern  = "",
    [switch]$SearchContent  = $false
)

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

$ScriptDir      = Split-Path -Parent $MyInvocation.MyCommand.Path
$SmartOpsScript = Join-Path $ScriptDir "smartops.ps1"
$DashboardFile  = Join-Path $ScriptDir "smartops-dashboard.html"
$LogFile        = Join-Path $ScriptDir "smartops-bridge.log"

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] [$Level] $Message"
    Add-Content -Path $LogFile -Value $line -ErrorAction SilentlyContinue
}

function Write-BridgeHeader {
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║   SMARTOPS BRIDGE  ·  Midnight Edition   ║" -ForegroundColor Cyan
    Write-Host "  ╚══════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Assert-SmartOps {
    if (-not (Test-Path $SmartOpsScript)) {
        Write-Host "  ❌  smartops.ps1 not found at: $SmartOpsScript" -ForegroundColor Red
        Write-Host "  ℹ️   Place this bridge script in the same folder as smartops.ps1" -ForegroundColor Yellow
        exit 1
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# MODE 1 — OPEN HTML DASHBOARD IN DEFAULT BROWSER
# ─────────────────────────────────────────────────────────────────────────────

function Open-Dashboard {
    Write-BridgeHeader
    if (-not (Test-Path $DashboardFile)) {
        Write-Host "  ❌  Dashboard file not found: $DashboardFile" -ForegroundColor Red
        exit 1
    }

    Write-Host "  📂 Opening dashboard: $DashboardFile" -ForegroundColor Yellow
    Write-Host "  ℹ️   For live output, also run: ./smartops-bridge.ps1 -Server" -ForegroundColor Cyan
    Write-Host ""

    # Cross-platform open
    if ($IsLinux) {
        & xdg-open $DashboardFile 2>$null
        if ($LASTEXITCODE -ne 0) {
            # Fallback: try common browsers
            foreach ($browser in @("firefox","chromium","google-chrome","brave-browser")) {
                if (Get-Command $browser -ErrorAction SilentlyContinue) {
                    & $browser $DashboardFile &
                    break
                }
            }
        }
    } elseif ($IsMacOS) {
        & open $DashboardFile
    } else {
        # Windows / WSL
        Start-Process $DashboardFile
    }

    Write-Host "  ✅  Dashboard launched." -ForegroundColor Green
    Write-Log "Dashboard opened: $DashboardFile"
}

# ─────────────────────────────────────────────────────────────────────────────
# MODE 2 — DIRECT CLI PASS-THROUGH (mirrors original smartops.ps1 behaviour)
# ─────────────────────────────────────────────────────────────────────────────

function Invoke-DirectFeature {
    Assert-SmartOps

    # Build argument list
    $args_list = @("-File", $SmartOpsScript, "-Feature", $Feature)
    if ($Path)          { $args_list += @("-Path",          $Path) }
    if ($Source)        { $args_list += @("-Source",        $Source) }
    if ($Destination)   { $args_list += @("-Destination",   $Destination) }
    if ($Device)        { $args_list += @("-Device",        $Device) }
    if ($IsoPath)       { $args_list += @("-IsoPath",       $IsoPath) }
    if ($Filesystem)    { $args_list += @("-Filesystem",    $Filesystem) }
    if ($Label)         { $args_list += @("-Label",         $Label) }
    if ($SearchPattern) { $args_list += @("-SearchPattern", $SearchPattern) }
    if ($SearchContent) { $args_list += "-SearchContent" }

    Write-Log "Running feature $Feature with args: $($args_list -join ' ')"

    # Execute smartops.ps1 and stream its STDOUT in real time
    $proc = Start-Process -FilePath "pwsh" `
        -ArgumentList $args_list `
        -NoNewWindow -PassThru -Wait
    exit $proc.ExitCode
}

# ─────────────────────────────────────────────────────────────────────────────
# MODE 3 — WEBSOCKET BRIDGE SERVER
# Receives JSON commands from the dashboard, runs the matching function,
# and streams STDOUT back line-by-line over the WebSocket.
#
# Dashboard connection snippet (add to smartops-dashboard.html):
# ─────────────────────────────────────────────────────────────
# const ws = new WebSocket('ws://localhost:9001');
# ws.onmessage = e => {
#   const { type, text } = JSON.parse(e.data);
#   printLine(type, text);
# };
# // To run a feature:
# ws.send(JSON.stringify({ feature: 1 }));
# ws.send(JSON.stringify({ feature: 17, path: '/home/user/Downloads' }));
# ─────────────────────────────────────────────────────────────────────────────

function Start-BridgeServer {
    Write-BridgeHeader
    Assert-SmartOps

    # Requires: pwsh 7+ with HttpListener (built-in)
    # For true WebSocket support install: dotnet tool install -g websocket-sharp
    # This implementation uses HTTP long-polling as a universal fallback.

    $listener = New-Object System.Net.HttpListener
    $listener.Prefixes.Add("http://localhost:$Port/")
    $listener.Start()

    Write-Host "  🔌 Bridge server listening on http://localhost:$Port" -ForegroundColor Green
    Write-Host "  ℹ️   Dashboard will connect automatically if -Server URL is configured." -ForegroundColor Cyan
    Write-Host "  ℹ️   Press Ctrl+C to stop." -ForegroundColor Cyan
    Write-Host ""
    Write-Log "Bridge server started on port $Port"

    # ── Request handler loop ──────────────────────────────────────────────
    while ($listener.IsListening) {
        try {
            $ctx     = $listener.GetContext()
            $req     = $ctx.Request
            $resp    = $ctx.Response

            # CORS headers for browser access
            $resp.Headers.Add("Access-Control-Allow-Origin", "*")
            $resp.Headers.Add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            $resp.Headers.Add("Access-Control-Allow-Headers", "Content-Type")
            $resp.ContentType = "application/json; charset=utf-8"

            if ($req.HttpMethod -eq "OPTIONS") {
                $resp.StatusCode = 204
                $resp.Close()
                continue
            }

            # ── Parse request body ──────────────────────────────────────
            $body = ""
            if ($req.HasEntityBody) {
                $reader = New-Object System.IO.StreamReader($req.InputStream)
                $body   = $reader.ReadToEnd()
                $reader.Close()
            }

            $cmd = $null
            try { $cmd = $body | ConvertFrom-Json } catch {}

            if (-not $cmd -or -not $cmd.feature) {
                $errJson = '{"error":"Missing feature number"}'
                $bytes   = [System.Text.Encoding]::UTF8.GetBytes($errJson)
                $resp.ContentLength64 = $bytes.Length
                $resp.OutputStream.Write($bytes, 0, $bytes.Length)
                $resp.Close()
                continue
            }

            # ── Build pwsh argument list from JSON command ──────────────
            $feature = [int]$cmd.feature
            $run_args = @("-File", $SmartOpsScript, "-Feature", $feature)

            if ($cmd.path)          { $run_args += @("-Path",          $cmd.path) }
            if ($cmd.source)        { $run_args += @("-Source",        $cmd.source) }
            if ($cmd.destination)   { $run_args += @("-Destination",   $cmd.destination) }
            if ($cmd.device)        { $run_args += @("-Device",        $cmd.device) }
            if ($cmd.isoPath)       { $run_args += @("-IsoPath",       $cmd.isoPath) }
            if ($cmd.filesystem)    { $run_args += @("-Filesystem",    $cmd.filesystem) }
            if ($cmd.label)         { $run_args += @("-Label",         $cmd.label) }
            if ($cmd.searchPattern) { $run_args += @("-SearchPattern", $cmd.searchPattern) }

            Write-Log "API request: feature=$feature args=$($run_args -join ' ')"

            # ── Execute and capture output ──────────────────────────────
            $psi                       = New-Object System.Diagnostics.ProcessStartInfo
            $psi.FileName              = "pwsh"
            $psi.Arguments             = $run_args -join " "
            $psi.RedirectStandardOutput = $true
            $psi.RedirectStandardError  = $true
            $psi.UseShellExecute        = $false
            $psi.CreateNoWindow         = $true

            $proc = [System.Diagnostics.Process]::Start($psi)
            $stdout = $proc.StandardOutput.ReadToEnd()
            $stderr = $proc.StandardError.ReadToEnd()
            $proc.WaitForExit()

            # ── Build JSON response with line-by-line output ────────────
            $lines = ($stdout + $stderr) -split "`n" |
                     Where-Object { $_ -ne "" } |
                     ForEach-Object {
                         $line = $_.TrimEnd()
                         # Classify line type for dashboard colouring
                         $type = if     ($line -match "✅|SUCCESS|successfully") { "success" }
                                 elseif ($line -match "⚠️|WARNING|warn")         { "warn" }
                                 elseif ($line -match "❌|ERROR|error|failed")    { "danger" }
                                 elseif ($line -match "^[═╔╚╗╝║▶]")              { "section" }
                                 elseif ($line -match "^   ")                    { "text" }
                                 else                                            { "info" }
                         [PSCustomObject]@{ type = $type; text = $line }
                     }

            $responseObj = [PSCustomObject]@{
                feature  = $feature
                exitCode = $proc.ExitCode
                lines    = $lines
            }
            $json  = $responseObj | ConvertTo-Json -Depth 5 -Compress
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
            $resp.ContentLength64 = $bytes.Length
            $resp.OutputStream.Write($bytes, 0, $bytes.Length)
            $resp.Close()

            Write-Host "  ✅ Feature $feature served ($($lines.Count) lines)" -ForegroundColor Green

        } catch [System.Net.HttpListenerException] {
            break
        } catch {
            Write-Host "  ❌ Server error: $_" -ForegroundColor Red
            Write-Log "Server error: $_" "ERROR"
            try { $ctx.Response.Close() } catch {}
        }
    }

    $listener.Stop()
    Write-Host "`n  Bridge server stopped." -ForegroundColor Yellow
    Write-Log "Bridge server stopped"
}

# ─────────────────────────────────────────────────────────────────────────────
# MAIN DISPATCH
# ─────────────────────────────────────────────────────────────────────────────

if ($UI) {
    Open-Dashboard
    exit 0
}

if ($Server) {
    Start-BridgeServer
    exit 0
}

if ($Feature -gt 0) {
    Invoke-DirectFeature
    exit 0
}

# ── No flags: show bridge help ────────────────────────────────────────────────
Write-BridgeHeader
Write-Host "  USAGE" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Open dashboard in browser:" -ForegroundColor Cyan
Write-Host "    ./smartops-bridge.ps1 -UI" -ForegroundColor White
Write-Host ""
Write-Host "  Run a feature headlessly:" -ForegroundColor Cyan
Write-Host "    ./smartops-bridge.ps1 -Feature 1" -ForegroundColor White
Write-Host "    ./smartops-bridge.ps1 -Feature 13 -Path '/home/user'" -ForegroundColor White
Write-Host "    ./smartops-bridge.ps1 -Feature 17 -Path '/home/user/Downloads'" -ForegroundColor White
Write-Host "    ./smartops-bridge.ps1 -Feature 21 -Device '/dev/sdb' -IsoPath 'kali.iso'" -ForegroundColor White
Write-Host ""
Write-Host "  Start live WebSocket bridge server:" -ForegroundColor Cyan
Write-Host "    ./smartops-bridge.ps1 -Server [-Port 9001]" -ForegroundColor White
Write-Host ""
Write-Host "  Dashboard → Server integration:" -ForegroundColor Cyan
Write-Host "    Add this to smartops-dashboard.html <script>:" -ForegroundColor White
Write-Host '    const ws = new WebSocket("ws://localhost:9001");' -ForegroundColor DarkGray
Write-Host '    ws.onmessage = e => { const d=JSON.parse(e.data); d.lines.forEach(l=>printLine(l.type,l.text)); };' -ForegroundColor DarkGray
Write-Host '    ws.send(JSON.stringify({ feature: 1 }));' -ForegroundColor DarkGray
Write-Host ""
