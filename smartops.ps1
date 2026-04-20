#!/usr/bin/env pwsh

# ============================================================
#  KALI SMARTOPS MANAGER PRO
#  System Administration Tool for Linux (PowerShell Core)
#  FIXED: Comprehensive trash deletion (files + info + expunged)
# ============================================================

param(
    [int]$Feature       = 0,
    [string]$Path       = "",
    [string]$Source     = "",
    [string]$Destination= "",
    [string]$Device     = "",
    [string]$IsoPath    = "",
    [string]$Filesystem = "ext4",
    [string]$Label      = "",
    [string]$SearchPattern = "",
    [switch]$SearchContent = $false,
    [switch]$DryRun     = $false,
    [switch]$SkipConfirm = $false
)

# ============================================
# SECTION: MENU DISPLAY
# ============================================

function Show-Menu {
    Clear-Host
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                              ║" -ForegroundColor Cyan
    Write-Host "║                    Kali Intelliops - CONSOLE                 ║" -ForegroundColor Yellow
    Write-Host "║                    System Administration Tool                ║" -ForegroundColor Green
    Write-Host "║                                                              ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "┌─────────────────────────────────────────────────────────────┐" -ForegroundColor Magenta
    Write-Host "│                    MAIN MENU                                │" -ForegroundColor Magenta
    Write-Host "├─────────────────────────────────────────────────────────────┤" -ForegroundColor Magenta
    Write-Host "│  1. 📊 System Information                                   │" -ForegroundColor Green
    Write-Host "│  2. 🔍 Process Monitor (Top 15)                            │" -ForegroundColor Green
    Write-Host "│  3. 📈 Real-time System Monitor                             │" -ForegroundColor Green
    Write-Host "│  4. 🌐 Network Interfaces & Connections                     │" -ForegroundColor Green
    Write-Host "│  5. 📡 Bandwidth Usage Statistics                           │" -ForegroundColor Green
    Write-Host "│  6. 🔒 Port Scan (Listening Ports)                          │" -ForegroundColor Green
    Write-Host "│  7. 🔄 Service Manager (Running/Failed)                     │" -ForegroundColor Green
    Write-Host "│  8. 💾 Disk Usage Analysis                                  │" -ForegroundColor Green
    Write-Host "│  9. 🧹 System Cleanup Tools                                 │" -ForegroundColor Green
    Write-Host "│ 10. 🔐 Security Check (Suspicious Processes)                │" -ForegroundColor Green
    Write-Host "│ 11. 📦 Package Manager Updates                              │" -ForegroundColor Green
    Write-Host "│ 12. 💻 Hardware Information                                 │" -ForegroundColor Green
    Write-Host "│ 13. 📁 File Manager (List Directory)                        │" -ForegroundColor Green
    Write-Host "│ 14. 💿 Bootable Drive Creator                               │" -ForegroundColor Green
    Write-Host "│ 15. 💾 Storage Format                                       │" -ForegroundColor Green
    Write-Host "│ 16. 🔍 File Search (Find Files)                             │" -ForegroundColor Green
    Write-Host "│ 17. 🗂️  Automated File Organizer                            │" -ForegroundColor Cyan
    Write-Host "│ 18. 🧽 Smart Cleaner (Cache/Temp/Trash/Duplicates)  FIXED   │" -ForegroundColor Yellow
    Write-Host "│  0. ❌ Exit Application                                     │" -ForegroundColor Red
    Write-Host "└─────────────────────────────────────────────────────────────┘" -ForegroundColor Magenta
    Write-Host ""
}

# ============================================
# SECTION 1: SYSTEM INFORMATION
# ============================================

function Show-SystemInfo {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    SYSTEM INFORMATION                         ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    Write-Host "`n▶ OPERATING SYSTEM:" -ForegroundColor Yellow
    $osInfo = & lsb_release -d 2>$null | cut -f2
    if (-not $osInfo) { $osInfo = & cat /etc/os-release 2>$null | grep PRETTY_NAME | cut -d'=' -f2 | tr -d '"' }
    Write-Host "   $osInfo" -ForegroundColor White

    Write-Host "`n▶ KERNEL:" -ForegroundColor Yellow
    Write-Host "   $(uname -a)" -ForegroundColor White

    Write-Host "`n▶ UPTIME:" -ForegroundColor Yellow
    $uptime = & uptime -p 2>$null
    if (-not $uptime) { $uptime = & uptime }
    Write-Host "   $uptime" -ForegroundColor White

    Write-Host "`n▶ CPU INFORMATION:" -ForegroundColor Yellow
    $cpuModel = & lscpu 2>$null | grep "Model name" | cut -d':' -f2 | xargs
    Write-Host "   Model: $cpuModel" -ForegroundColor White
    $cpuCores = & nproc 2>$null
    if (-not $cpuCores) { $cpuCores = & grep -c ^processor /proc/cpuinfo }
    Write-Host "   Cores: $cpuCores" -ForegroundColor White
    Write-Host "   Architecture: $(uname -m)" -ForegroundColor White

    Write-Host "`n▶ MEMORY USAGE:" -ForegroundColor Yellow
    & free -h | grep -E "^(Mem|Swap)" | ForEach-Object { Write-Host "   $_" -ForegroundColor White }

    Write-Host "`n▶ DISK USAGE:" -ForegroundColor Yellow
    & df -h | grep -E "^/dev/" | ForEach-Object { Write-Host "   $_" -ForegroundColor White }

    Write-Host "`n▶ ACTIVE USERS:" -ForegroundColor Yellow
    & who | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
}

# ============================================
# SECTION 2: PROCESS MONITOR
# ============================================

function Show-ProcessMonitor {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║              TOP 15 PROCESSES BY CPU & MEMORY                  ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host ("{0,-8} {1,-25} {2,-10} {3,-10} {4,-15}" -f "PID","PROCESS","CPU%","MEM%","USER") -ForegroundColor Yellow
    Write-Host ("{0,-8} {1,-25} {2,-10} {3,-10} {4,-15}" -f "---","-------","----","----","----") -ForegroundColor DarkGray

    $processes = & ps -eo pid,comm,%cpu,%mem,user --sort=-%cpu 2>$null | head -16
    if (-not $processes) { $processes = & ps aux 2>$null | sort -k3 -rn | head -16 }
    $processes | Select-Object -Skip 1 | ForEach-Object {
        $fields = $_ -split '\s+', 5
        if ($fields.Count -ge 5) {
            Write-Host ("{0,-8} {1,-25} {2,-10} {3,-10} {4,-15}" -f $fields[0],$fields[1],$fields[2],$fields[3],$fields[4]) -ForegroundColor White
        }
    }
    $totalProc = & ps -e 2>$null | Measure-Object -Line | Select-Object -ExpandProperty Lines
    Write-Host "`n📊 Total Running Processes: $totalProc" -ForegroundColor Green
}

# ============================================
# SECTION 3: REAL-TIME SYSTEM MONITOR
# ============================================

function Show-RealtimeMonitor {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                 REAL-TIME SYSTEM METRICS                       ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    $cpuLine = & top -bn1 2>$null | grep "Cpu(s)"
    if (-not $cpuLine) { $cpuLine = & top -bn1 2>$null | grep "%Cpu" }
    if ($cpuLine -match "([0-9.]+)%") { $cpuLoad = $matches[1] } else { $cpuLoad = "0" }

    Write-Host "`n▶ CPU USAGE:" -ForegroundColor Yellow
    $cpuInt = [int][math]::Floor($cpuLoad)
    if ($cpuInt -gt 80)     { Write-Host "   ⚠️  ${cpuLoad}% (HIGH USAGE!)" -ForegroundColor Red }
    elseif ($cpuInt -gt 60) { Write-Host "   ⚡ ${cpuLoad}% (Moderate)" -ForegroundColor Yellow }
    else                    { Write-Host "   ✅ ${cpuLoad}% (Normal)" -ForegroundColor Green }

    $memInfo = & free 2>$null | grep Mem
    if ($memInfo) {
        $memParts = $memInfo -split '\s+'
        $memTotal = $memParts[1]; $memUsed = $memParts[2]
        $memUsage = [math]::Round(($memUsed / $memTotal) * 100, 1)
        Write-Host "`n▶ MEMORY USAGE:" -ForegroundColor Yellow
        if ($memUsage -gt 90)     { Write-Host "   ⚠️  $memUsage% (CRITICAL!)" -ForegroundColor Red }
        elseif ($memUsage -gt 75) { Write-Host "   ⚡ $memUsage% (High)" -ForegroundColor Yellow }
        else                      { Write-Host "   ✅ $memUsage% (Normal)" -ForegroundColor Green }
    }

    $diskInfo = & df -h / 2>$null | tail -1
    if ($diskInfo) {
        $diskParts = $diskInfo -split '\s+'
        $diskUsage = $diskParts[4] -replace '%',''
        Write-Host "`n▶ DISK USAGE (/):" -ForegroundColor Yellow
        $diskInt = [int]$diskUsage
        if ($diskInt -gt 85)     { Write-Host "   ⚠️  ${diskUsage}% (LOW SPACE!)" -ForegroundColor Red }
        elseif ($diskInt -gt 70) { Write-Host "   ⚡ ${diskUsage}% (Getting Full)" -ForegroundColor Yellow }
        else                     { Write-Host "   ✅ ${diskUsage}% (Good)" -ForegroundColor Green }
    }

    $loadAvg = & uptime 2>$null
    if ($loadAvg) { Write-Host "`n▶ LOAD AVERAGE:" -ForegroundColor Yellow; Write-Host "   $loadAvg" -ForegroundColor White }
}

# ============================================
# SECTION 4: NETWORK INTERFACES
# ============================================

function Show-NetworkInfo {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                   NETWORK INTERFACES                           ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    Write-Host "`n▶ ACTIVE NETWORK INTERFACES:" -ForegroundColor Yellow
    $interfaces = & ip -br addr show 2>$null
    if ($interfaces) {
        $interfaces | ForEach-Object {
            if ($_ -match "UP") { Write-Host "   ✅ $_" -ForegroundColor Green }
            else                { Write-Host "   ❌ $_" -ForegroundColor Red }
        }
    }

    Write-Host "`n▶ ACTIVE CONNECTIONS:" -ForegroundColor Yellow
    $connCount = & ss -tuln 2>$null | Measure-Object -Line | Select-Object -ExpandProperty Lines
    Write-Host "   $connCount listening ports" -ForegroundColor White

    Write-Host "`n▶ DETAILED CONNECTIONS (First 20):" -ForegroundColor Yellow
    & ss -tuln 2>$null | Select-Object -First 20 | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
}

# ============================================
# SECTION 5: BANDWIDTH STATISTICS
# ============================================

function Show-Bandwidth {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                   BANDWIDTH STATISTICS                         ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    $interfaces = & ip -br link 2>$null | grep -v LOOPBACK | awk '{print $1}'
    foreach ($iface in $interfaces) {
        $rx_bytes = & cat "/sys/class/net/$iface/statistics/rx_bytes" 2>$null
        $tx_bytes = & cat "/sys/class/net/$iface/statistics/tx_bytes" 2>$null
        if ($rx_bytes -and $tx_bytes) {
            $rx_gb = [math]::Round($rx_bytes / 1024 / 1024 / 1024, 2)
            $tx_gb = [math]::Round($tx_bytes / 1024 / 1024 / 1024, 2)
            Write-Host "▶ INTERFACE: $iface" -ForegroundColor Yellow
            Write-Host "   📥 Received: $rx_gb GB" -ForegroundColor White
            Write-Host "   📤 Transmitted: $tx_gb GB" -ForegroundColor White
        }
    }
}

# ============================================
# SECTION 6: PORT SCAN
# ============================================

function Show-PortScan {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                   LISTENING PORTS                              ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    Write-Host "`n▶ OPEN PORTS (LISTENING):" -ForegroundColor Yellow
    $ports = & ss -tuln 2>$null | grep LISTEN | awk '{print $5}' | cut -d':' -f2 | sort -n | uniq
    $ports | ForEach-Object {
        $port = $_
        $service = switch ($port) {
            "22"   { "SSH" } "80" { "HTTP" } "443" { "HTTPS" }
            "3306" { "MySQL" } "5432" { "PostgreSQL" } "8080" { "HTTP-Alt" }
            "53"   { "DNS" } "25" { "SMTP" } "21" { "FTP" }
            default { "Unknown" }
        }
        Write-Host "   🔌 Port $port - $service" -ForegroundColor Green
    }

    Write-Host "`n▶ DETAILED LISTENING SERVICES:" -ForegroundColor Yellow
    & ss -tuln 2>$null | grep LISTEN | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
}

# ============================================
# SECTION 7: SERVICE MANAGER
# ============================================

function Show-ServiceManager {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    SERVICE MANAGER                             ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    Write-Host "`n▶ RUNNING SERVICES (First 20):" -ForegroundColor Green
    $running = & systemctl list-units --type=service --state=running 2>$null | head -20
    if ($running) { $running | ForEach-Object { Write-Host "   ✅ $_" -ForegroundColor White } }
    else          { Write-Host "   ⚠️  No running services found or systemctl not available" -ForegroundColor Yellow }

    Write-Host "`n▶ FAILED SERVICES:" -ForegroundColor Red
    $failed = & systemctl --failed 2>$null | grep -E "^●" | head -10
    if ($failed) { $failed | ForEach-Object { Write-Host "   ❌ $_" -ForegroundColor Red } }
    else         { Write-Host "   ✅ No failed services found" -ForegroundColor Green }
}

# ============================================
# SECTION 8: DISK USAGE ANALYSIS
# ============================================

function Show-DiskAnalysis {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                   DISK USAGE ANALYSIS                          ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    Write-Host "`n▶ LARGEST DIRECTORIES IN /HOME (Top 10):" -ForegroundColor Yellow
    $homeDirs = & du -h /home 2>$null | sort -rh | head -10
    if ($homeDirs) { $homeDirs | ForEach-Object { Write-Host "   📁 $_" -ForegroundColor White } }
    else           { Write-Host "   No home directories found or insufficient permissions" -ForegroundColor Gray }

    Write-Host "`n▶ LARGEST DIRECTORIES IN CURRENT DIRECTORY (Top 10):" -ForegroundColor Yellow
    & du -h --max-depth=2 2>$null | sort -rh | head -10 | ForEach-Object { Write-Host "   📁 $_" -ForegroundColor White }

    Write-Host "`n▶ DISK USAGE BY FILE TYPE:" -ForegroundColor Yellow
    Write-Host "   Videos:    $(find . -name '*.mp4' -o -name '*.avi' -o -name '*.mkv' 2>$null | wc -l) files" -ForegroundColor White
    Write-Host "   Images:    $(find . -name '*.jpg' -o -name '*.png' -o -name '*.gif' 2>$null | wc -l) files" -ForegroundColor White
    Write-Host "   Documents: $(find . -name '*.pdf' -o -name '*.doc' -o -name '*.txt' 2>$null | wc -l) files" -ForegroundColor White
    Write-Host "   Archives:  $(find . -name '*.zip' -o -name '*.tar.gz' -o -name '*.rar' 2>$null | wc -l) files" -ForegroundColor White
}

# ============================================
# SECTION 9: SYSTEM CLEANUP TOOLS
# ============================================

function Show-CleanupTools {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    SYSTEM CLEANUP TOOLS                        ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    $cacheSize = & du -sh /var/cache/apt/archives 2>$null | awk '{print $1}'
    if (-not $cacheSize) { $cacheSize = "0B" }
    Write-Host "`n▶ PACKAGE CACHE:" -ForegroundColor Yellow
    Write-Host "   Size: $cacheSize" -ForegroundColor White

    $logCount = & find /var/log -name "*.log" -mtime +30 2>$null | wc -l
    Write-Host "`n▶ OLD LOG FILES (>30 days):" -ForegroundColor Yellow
    Write-Host "   Files found: $logCount" -ForegroundColor White

    $tmpSize = & du -sh /tmp 2>$null | awk '{print $1}'
    Write-Host "`n▶ TEMPORARY FILES:" -ForegroundColor Yellow
    Write-Host "   /tmp size: $tmpSize" -ForegroundColor White

    $trashSize = & du -sh ~/.local/share/Trash 2>$null | awk '{print $1}'
    Write-Host "`n▶ TRASH SIZE:" -ForegroundColor Yellow
    Write-Host "   $trashSize" -ForegroundColor White
}

# ============================================
# SECTION 10: SECURITY CHECK
# ============================================

function Show-SecurityCheck {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    SECURITY CHECK                              ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    Write-Host "`n▶ SUSPICIOUS PROCESSES (High CPU > 80%):" -ForegroundColor Yellow
    $highCpu      = & ps -eo pid,comm,%cpu --sort=-%cpu 2>$null | head -10
    $foundHighCpu = $false
    $highCpu | ForEach-Object {
        if ($_ -match "([8-9][0-9]|100)") { Write-Host "   ⚠️  $_" -ForegroundColor Red; $foundHighCpu = $true }
        elseif ($_ -notmatch "PID")       { Write-Host "   $_" -ForegroundColor White }
    }
    if (-not $foundHighCpu) { Write-Host "   ✅ No suspicious high-CPU processes found" -ForegroundColor Green }

    Write-Host "`n▶ LAST LOGINS (First 10):" -ForegroundColor Yellow
    & last -n 10 2>$null | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
}

# ============================================
# SECTION 11: PACKAGE UPDATES
# ============================================

function Show-PackageUpdates {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    PACKAGE UPDATES                             ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    Write-Host "`n▶ UPDATING PACKAGE LIST..." -ForegroundColor Yellow
    & sudo apt-get update 2>&1 | tail -5

    Write-Host "`n▶ AVAILABLE UPDATES:" -ForegroundColor Yellow
    $updates = & apt list --upgradable 2>$null | grep -v "Listing" | Select-Object -First 20
    if ($updates) {
        $updates | ForEach-Object { Write-Host "   📦 $_" -ForegroundColor White }
        $updateCount = ($updates | Measure-Object -Line).Lines
        Write-Host "`n📊 Total updates available: $updateCount" -ForegroundColor Green
    } else {
        Write-Host "   ✅ System is up to date!" -ForegroundColor Green
    }
}

# ============================================
# SECTION 12: HARDWARE INFORMATION
# ============================================

function Show-HardwareInfo {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                   HARDWARE INFORMATION                         ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    Write-Host "`n▶ CPU DETAILS:" -ForegroundColor Yellow
    & lscpu 2>$null | grep -E "^(Model name|Architecture|CPU\(s\)|Thread|Core|Socket|Virtualization)" |
        ForEach-Object { Write-Host "   $_" -ForegroundColor White }

    Write-Host "`n▶ MEMORY DETAILS:" -ForegroundColor Yellow
    & free -h | head -2 | ForEach-Object { Write-Host "   $_" -ForegroundColor White }

    Write-Host "`n▶ BLOCK DEVICES (Drives):" -ForegroundColor Yellow
    & lsblk 2>$null | grep -v "loop" | head -15 | ForEach-Object { Write-Host "   💾 $_" -ForegroundColor White }

    Write-Host "`n▶ GRAPHICS CARD:" -ForegroundColor Yellow
    & lspci 2>$null | grep -i "vga" | ForEach-Object { Write-Host "   🖥️  $_" -ForegroundColor White }

    Write-Host "`n▶ NETWORK CARDS:" -ForegroundColor Yellow
    & lspci 2>$null | grep -i "network" | ForEach-Object { Write-Host "   🌐 $_" -ForegroundColor White }
}

# ============================================
# SECTION 13: FILE MANAGER
# ============================================

function Get-FileList {
    param([string]$Directory)
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    FILE LIST                                  ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host "`n📍 Directory: $Directory" -ForegroundColor Yellow
    Write-Host ""
    Write-Host ("{0,-10} {1,-35} {2,-15} {3,-20}" -f "TYPE","NAME","SIZE","MODIFIED") -ForegroundColor Green
    Write-Host ("{0,-10} {1,-35} {2,-15} {3,-20}" -f "----","----","----","--------") -ForegroundColor DarkGray

    $items = Get-ChildItem -Path $Directory -ErrorAction SilentlyContinue
    foreach ($item in $items) {
        $type     = if ($item.PSIsContainer) { "📁 DIR" } else { "📄 FILE" }
        $size     = if ($item.PSIsContainer) { "-" } else { "{0:N2} KB" -f ($item.Length / 1KB) }
        $modified = $item.LastWriteTime.ToString("yyyy-MM-dd HH:mm")
        $name     = if ($item.Name.Length -gt 32) { $item.Name.Substring(0,29) + "..." } else { $item.Name }
        Write-Host ("{0,-10} {1,-35} {2,-15} {3,-20}" -f $type,$name,$size,$modified) -ForegroundColor White
    }
    Write-Host "`n📊 Total items: $($items.Count)" -ForegroundColor Green
}

function Copy-ItemPS {
    param([string]$Source, [string]$Destination)
    Write-Host "`n📋 Copying..." -ForegroundColor Yellow
    try {
        if (Test-Path $Source -PathType Container) { Copy-Item -Path $Source -Destination $Destination -Recurse -Force }
        else { Copy-Item -Path $Source -Destination $Destination -Force }
        Write-Host "✅ Successfully copied!" -ForegroundColor Green
    } catch { Write-Host "❌ Error: $_" -ForegroundColor Red }
}

function Move-ItemPS {
    param([string]$Source, [string]$Destination)
    Write-Host "`n✂️ Moving..." -ForegroundColor Yellow
    try { Move-Item -Path $Source -Destination $Destination -Force; Write-Host "✅ Successfully moved!" -ForegroundColor Green }
    catch { Write-Host "❌ Error: $_" -ForegroundColor Red }
}

function Delete-ItemPS {
    param([string]$Path)
    Write-Host "`n🗑️ Deleting..." -ForegroundColor Yellow
    try {
        if (Test-Path $Path -PathType Container) { Remove-Item -Path $Path -Recurse -Force }
        else { Remove-Item -Path $Path -Force }
        Write-Host "✅ Successfully deleted!" -ForegroundColor Green
    } catch { Write-Host "❌ Error: $_" -ForegroundColor Red }
}

function Rename-ItemPS {
    param([string]$Path, [string]$NewName)
    Write-Host "`n✏️ Renaming..." -ForegroundColor Yellow
    try { Rename-Item -Path $Path -NewName $NewName -Force; Write-Host "✅ Successfully renamed!" -ForegroundColor Green }
    catch { Write-Host "❌ Error: $_" -ForegroundColor Red }
}

function New-FolderPS {
    param([string]$Path)
    Write-Host "`n📁 Creating folder..." -ForegroundColor Yellow
    try { New-Item -Path $Path -ItemType Directory -Force -ErrorAction Stop; Write-Host "✅ Folder created successfully!" -ForegroundColor Green }
    catch { Write-Host "❌ Error: $_" -ForegroundColor Red }
}

# ============================================
# SECTION 14: BOOTABLE DRIVE CREATOR
# ============================================

function Get-USBDrives {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    USB DRIVES                                 ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    $drives = Get-Disk | Where-Object { $_.BusType -eq "USB" -or $_.Size -lt 64GB }
    if ($drives) {
        foreach ($drive in $drives) {
            $size = [math]::Round($drive.Size / 1GB, 2)
            $friendlyName = if ($drive.FriendlyName) { $drive.FriendlyName } else { "USB Drive" }
            Write-Host "💾 Disk $($drive.Number): $friendlyName - ${size}GB" -ForegroundColor Green
            Write-Host "   Device: /dev/sd$(($drive.Number + 97) -as [char])" -ForegroundColor White
        }
    } else {
        Write-Host "⚠️ No USB drives detected" -ForegroundColor Yellow
    }
}

function Create-BootableDrive {
    param([string]$Device, [string]$IsoPath)
    Write-Host "`n⚠️  WARNING: This will DESTROY ALL DATA on $Device!" -ForegroundColor Red
    if (-not (Test-Path $Device))  { Write-Host "❌ Error: Device $Device does not exist!"   -ForegroundColor Red; return }
    if (-not (Test-Path $IsoPath)) { Write-Host "❌ Error: ISO file $IsoPath does not exist!" -ForegroundColor Red; return }
    try {
        $deviceBase = $Device -replace '[0-9]+$', ''
        sudo umount ${deviceBase}* 2>$null
        $process = Start-Process -NoNewWindow -Wait -PassThru -FilePath "sudo" `
            -ArgumentList "dd if=`"$IsoPath`" of=`"$Device`" bs=4M status=progress"
        if ($process.ExitCode -eq 0) { Write-Host "`n✅ Bootable USB created successfully!" -ForegroundColor Green }
        else                         { Write-Host "`n❌ Error creating bootable drive" -ForegroundColor Red }
    } catch { Write-Host "❌ Error: $_" -ForegroundColor Red }
}

# ============================================
# SECTION 15: STORAGE FORMAT
# ============================================

function Get-StorageDevices {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    STORAGE DEVICES                            ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    $disks = Get-Disk
    foreach ($disk in $disks) {
        $size       = [math]::Round($disk.Size / 1GB, 2)
        $type       = if ($disk.BusType -eq "USB") { "USB Drive" } else { "Internal Drive" }
        $devicePath = "/dev/sd$(($disk.Number + 97) -as [char])"
        Write-Host "💾 Disk $($disk.Number): $($disk.FriendlyName)" -ForegroundColor Green
        Write-Host "   Size: ${size}GB | Type: $type | Device: $devicePath" -ForegroundColor White
        $partitions = Get-Partition -DiskNumber $disk.Number -ErrorAction SilentlyContinue
        foreach ($part in $partitions) {
            $partSize    = [math]::Round($part.Size / 1GB, 2)
            $driveLetter = if ($part.DriveLetter) { "$($part.DriveLetter):" } else { "No letter" }
            Write-Host "   └─ Partition $($part.PartitionNumber): $driveLetter - ${partSize}GB" -ForegroundColor Gray
        }
    }
}

function Format-Storage {
    param([string]$Device, [string]$Filesystem, [string]$Label)
    Write-Host "`n⚠️  WARNING: This will DESTROY ALL DATA on $Device!" -ForegroundColor Red
    if (-not (Test-Path $Device)) { Write-Host "❌ Error: Device $Device does not exist!" -ForegroundColor Red; return }
    try {
        sudo umount $Device 2>$null
        switch ($Filesystem) {
            "ext4"  { if ($Label) { sudo mkfs.ext4 -F -L $Label $Device } else { sudo mkfs.ext4 -F $Device } }
            "ntfs"  { if ($Label) { sudo mkfs.ntfs -F -L $Label $Device } else { sudo mkfs.ntfs -F $Device } }
            "fat32" { if ($Label) { sudo mkfs.fat -F 32 -n $Label $Device } else { sudo mkfs.fat -F 32 $Device } }
            "exfat" { if ($Label) { sudo mkfs.exfat -n $Label $Device } else { sudo mkfs.exfat $Device } }
            default { Write-Host "❌ Unsupported filesystem: $Filesystem" -ForegroundColor Red; return }
        }
        Write-Host "✅ Device formatted successfully as $Filesystem!" -ForegroundColor Green
    } catch { Write-Host "❌ Error: $_" -ForegroundColor Red }
}

# ============================================
# SECTION 16: FILE SEARCH
# ============================================

function Find-FileByName {
    param([string]$SearchPattern, [string]$StartPath = ".")
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    FILE SEARCH RESULTS                        ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host "`n🔍 Searching for: *$SearchPattern*" -ForegroundColor Yellow
    Write-Host "📍 Starting from: $StartPath" -ForegroundColor Yellow

    try {
        $foundFiles = Get-ChildItem -Path $StartPath -Filter "*$SearchPattern*" -Recurse -File -ErrorAction SilentlyContinue
        if ($foundFiles.Count -eq 0) { Write-Host "`n❌ No files found matching the pattern" -ForegroundColor Red }
        else {
            Write-Host ("{0,-60} {1,-15} {2}" -f "FULL PATH","SIZE","MODIFIED") -ForegroundColor Green
            $counter = 0
            foreach ($file in $foundFiles) {
                $pathDisplay = if ($file.FullName.Length -gt 57) { "..." + $file.FullName.Substring($file.FullName.Length - 57) } else { $file.FullName }
                $sizeDisplay = "{0:N2} KB" -f ($file.Length / 1KB)
                $modified    = $file.LastWriteTime.ToString("yyyy-MM-dd HH:mm")
                Write-Host ("{0,-60} {1,-15} {2}" -f $pathDisplay,$sizeDisplay,$modified) -ForegroundColor White
                $counter++
                if ($counter -ge 50) { Write-Host "`n... (showing first 50 of $($foundFiles.Count) total)" -ForegroundColor Yellow; break }
            }
            Write-Host "`n📊 Total files found: $($foundFiles.Count)" -ForegroundColor Green
        }
    } catch { Write-Host "❌ Error searching files: $_" -ForegroundColor Red }
}

# ============================================
# SECTION 17: AUTOMATED FILE ORGANIZER
# ============================================

function Invoke-FileOrganizer {
    param([string]$TargetDirectory = ".")
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                  AUTOMATED FILE ORGANIZER                     ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    $TargetDirectory = (Resolve-Path $TargetDirectory -ErrorAction SilentlyContinue).Path
    if (-not $TargetDirectory) { Write-Host "❌ Directory not found." -ForegroundColor Red; return }
    Write-Host "`n📍 Organizing: $TargetDirectory" -ForegroundColor Yellow

    $ImagesDir    = "Images"; $DocumentsDir = "Documents"; $VideosDir = "Videos"
    $MusicDir     = "Music";  $ArchivesDir  = "Archives"

    foreach ($folder in @($ImagesDir,$DocumentsDir,$VideosDir,$MusicDir,$ArchivesDir)) {
        New-Item -Path (Join-Path $TargetDirectory $folder) -ItemType Directory -Force -ErrorAction SilentlyContinue | Out-Null
    }

    $movedCount = 0; $skippedCount = 0
    $allItems = Get-ChildItem -Path $TargetDirectory -ErrorAction SilentlyContinue

    foreach ($item in $allItems) {
        if ($item.PSIsContainer) { continue }
        if ($item.Name -eq (Split-Path $PSCommandPath -Leaf)) { $skippedCount++; continue }
        $ext = $item.Extension.TrimStart('.').ToLower()
        if ([string]::IsNullOrWhiteSpace($ext)) { Write-Host "[SKIP]     '$($item.Name)'" -ForegroundColor DarkGray; $skippedCount++; continue }

        $destinationFolder = switch ($ext) {
            { $_ -in @("jpg","jpeg","png","gif","svg","webp") }                          { Write-Host "[IMAGE]    '$($item.Name)'" -ForegroundColor Cyan;    $ImagesDir;    break }
            { $_ -in @("pdf","doc","docx","txt","ppt","pptx","xls","xlsx") }             { Write-Host "[DOCUMENT] '$($item.Name)'" -ForegroundColor Blue;    $DocumentsDir; break }
            { $_ -in @("mp4","mkv","mov","avi") }                                        { Write-Host "[VIDEO]    '$($item.Name)'" -ForegroundColor Magenta; $VideosDir;    break }
            { $_ -in @("mp3","wav","flac") }                                             { Write-Host "[MUSIC]    '$($item.Name)'" -ForegroundColor Green;   $MusicDir;     break }
            { $_ -in @("zip","rar","tar","gz") }                                         { Write-Host "[ARCHIVE]  '$($item.Name)'" -ForegroundColor Yellow;  $ArchivesDir;  break }
            default                                                                      { Write-Host "[SKIP]     '$($item.Name)' — unknown (.$ext)" -ForegroundColor DarkGray; $skippedCount++; $null }
        }

        if ($destinationFolder) {
            try { Move-Item -Path $item.FullName -Destination (Join-Path $TargetDirectory $destinationFolder) -Force -ErrorAction Stop; $movedCount++ }
            catch { Write-Host "   ❌ Failed: $_" -ForegroundColor Red; $skippedCount++ }
        }
    }

    Write-Host "`n✅ Done! Moved: $movedCount  Skipped: $skippedCount" -ForegroundColor Green
}

# ================================================================
# HELPER: Get human-readable file size
# ================================================================

function Get-HumanSize {
    param([long]$Bytes)
    if ($Bytes -ge 1GB) { return "{0:N2} GB" -f ($Bytes / 1GB) }
    if ($Bytes -ge 1MB) { return "{0:N2} MB" -f ($Bytes / 1MB) }
    if ($Bytes -ge 1KB) { return "{0:N2} KB" -f ($Bytes / 1KB) }
    return "$Bytes B"
}

# ================================================================
# HELPER: Delete ALL contents inside a directory (not the dir itself)
# Returns hashtable: @{ Removed=N; Freed=N; Errors=@(...) }
# ================================================================

function Remove-DirectoryContents {
    param([string]$DirPath)

    $result = @{ Removed = 0; Freed = [long]0; Errors = @() }

    if (-not (Test-Path $DirPath)) { return $result }

    $items = Get-ChildItem -Path $DirPath -Force -ErrorAction SilentlyContinue
    foreach ($item in $items) {
        try {
            $sz = [long]0
            if ($item.PSIsContainer) {
                # Sum size before removal
                $sz = (Get-ChildItem -Path $item.FullName -Recurse -Force -File -ErrorAction SilentlyContinue |
                       Measure-Object -Property Length -Sum).Sum
                if (-not $sz) { $sz = 0 }
                Remove-Item -Path $item.FullName -Recurse -Force -ErrorAction Stop
            } else {
                $sz = $item.Length
                Remove-Item -Path $item.FullName -Force -ErrorAction Stop
            }
            $result.Removed++
            $result.Freed += $sz
        } catch {
            $result.Errors += "Could not delete '$($item.Name)': $_"
        }
    }
    return $result
}

# ================================================================
# HELPER: Empty trash COMPLETELY
# Removes: files/, info/ (.trashinfo), expunged/, directorysizes
# Works for current user, root, and any /home/* user (if accessible)
# ================================================================

function Invoke-EmptyTrash {
    param([switch]$SkipConfirm)

    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                  🗑️  EMPTY TRASH (COMPLETE)                   ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    # Collect all trash root directories to process
    $trashRoots = [System.Collections.Generic.List[string]]::new()

    # Current user's trash
    $userTrash = "$HOME/.local/share/Trash"
    if (Test-Path $userTrash) { $trashRoots.Add($userTrash) }

    # Root's trash (if different)
    $rootTrash = "/root/.local/share/Trash"
    if ((Test-Path $rootTrash) -and ($rootTrash -ne $userTrash)) {
        $trashRoots.Add($rootTrash)
    }

    # Other users' trash folders
    if (Test-Path "/home") {
        Get-ChildItem -Path "/home" -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $ut = "$($_.FullName)/.local/share/Trash"
            if ((Test-Path $ut) -and ($ut -ne $userTrash)) {
                $trashRoots.Add($ut)
            }
        }
    }

    if ($trashRoots.Count -eq 0) {
        Write-Host "   ✅ No trash directories found — already clean!" -ForegroundColor Green
        return
    }

    # Show what we found
    Write-Host "`n▶ TRASH LOCATIONS FOUND:" -ForegroundColor Yellow
    $grandTotalEst = [long]0
    foreach ($tr in $trashRoots) {
        $est = (Get-ChildItem -Path $tr -Recurse -Force -File -ErrorAction SilentlyContinue |
                Measure-Object -Property Length -Sum).Sum
        if (-not $est) { $est = 0 }
        $grandTotalEst += $est
        Write-Host ("   {0,-55} {1}" -f $tr, (Get-HumanSize -Bytes $est)) -ForegroundColor White
    }
    Write-Host ""
    Write-Host "   TOTAL ESTIMATED SIZE: $(Get-HumanSize -Bytes $grandTotalEst)" -ForegroundColor Yellow

    if (-not $SkipConfirm) {
        Write-Host ""
        Write-Host "   ⚠️  This will permanently delete ALL files in the above trash locations." -ForegroundColor Red
        Write-Host "   Type YES to confirm: " -ForegroundColor Yellow -NoNewline
        $answer = Read-Host
        if ($answer -ne "YES") {
            Write-Host "`n   ❌ Cancelled. No files were deleted." -ForegroundColor Gray
            return
        }
    }

    Write-Host ""
    $grandRemoved = 0
    $grandFreed   = [long]0

    foreach ($tr in $trashRoots) {
        Write-Host "   🗑️  Processing: $tr" -ForegroundColor Yellow

        # Sub-directories to clear: files, info, expunged
        # Also delete any loose files at the root (e.g., directorysizes)
        $subDirs   = @("files", "info", "expunged")
        $trRemoved = 0
        $trFreed   = [long]0

        foreach ($sub in $subDirs) {
            $subPath = Join-Path $tr $sub
            if (Test-Path $subPath) {
                $r = Remove-DirectoryContents -DirPath $subPath
                $trRemoved += $r.Removed
                $trFreed   += $r.Freed
                if ($r.Errors.Count -gt 0) {
                    $r.Errors | Select-Object -First 3 | ForEach-Object {
                        Write-Host "     ⚠  $_" -ForegroundColor Yellow
                    }
                }
                Write-Host ("     ✅ {0,-15} cleared — {1} items, {2}" -f $sub, $r.Removed, (Get-HumanSize -Bytes $r.Freed)) -ForegroundColor Green
            } else {
                Write-Host ("     ○  {0,-15} not found (skipped)" -f $sub) -ForegroundColor DarkGray
            }
        }

        # Remove loose metadata files at trash root level (e.g., directorysizes)
        $looseFiles = Get-ChildItem -Path $tr -File -Force -ErrorAction SilentlyContinue
        foreach ($lf in $looseFiles) {
            try {
                $sz = $lf.Length
                Remove-Item -Path $lf.FullName -Force -ErrorAction Stop
                $trRemoved++; $trFreed += $sz
            } catch {
                Write-Host "     ⚠  Could not remove '$($lf.Name)': $_" -ForegroundColor Yellow
            }
        }

        $grandRemoved += $trRemoved
        $grandFreed   += $trFreed
    }

    Write-Host ""
    Write-Host "──────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
    Write-Host "   ✅ TRASH EMPTY COMPLETE" -ForegroundColor Green
    Write-Host "   Items removed  : $grandRemoved" -ForegroundColor White
    Write-Host "   Space freed    : $(Get-HumanSize -Bytes $grandFreed)" -ForegroundColor White
    Write-Host "──────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
}

# ================================================================
# SECTION 18: SMART CLEANER — Cache / Temp / Trash / Duplicates
# ================================================================

function Invoke-SmartCleaner {
    param(
        [string]$Mode = "SCAN",     # SCAN | CLEAN | DUPES | DEL_DUPES | EMPTY_TRASH
        [string]$ScanPath = "",
        [switch]$DryRun,
        [switch]$SkipConfirm
    )

    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                   🧽 SMART CLEANER                            ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

    # ── EMPTY TRASH mode ───────────────────────────────────────────
    if ($Mode -eq "EMPTY_TRASH") {
        Invoke-EmptyTrash -SkipConfirm:$SkipConfirm
        return
    }

    # ── SCAN / CLEAN mode ──────────────────────────────────────────
    if ($Mode -eq "SCAN" -or $Mode -eq "CLEAN") {

        # Define all target paths. Note: Trash includes BOTH files/ and info/
        $targets = @(
            @{ Label="APT Package Cache";       Path="/var/cache/apt/archives";                        SubDir=$false }
            @{ Label="APT Lists Cache";          Path="/var/lib/apt/lists";                             SubDir=$false }
            @{ Label="Temp Files (/tmp)";        Path="/tmp";                                           SubDir=$false }
            @{ Label="User Cache (~/.cache)";    Path="$HOME/.cache";                                  SubDir=$false }
            @{ Label="Thumbnail Cache";          Path="$HOME/.cache/thumbnails";                       SubDir=$false }
            @{ Label="Old Journal Logs";         Path="/var/log/journal";                               SubDir=$false }
            @{ Label="Compressed Logs";          Path="/var/log";                                       SubDir=$false; Filter="*.gz" }
            @{ Label="Trash — Files";            Path="$HOME/.local/share/Trash/files";                SubDir=$false }
            @{ Label="Trash — Metadata (.info)"; Path="$HOME/.local/share/Trash/info";                 SubDir=$false }
            @{ Label="Trash — Expunged";         Path="$HOME/.local/share/Trash/expunged";             SubDir=$false }
        )

        $grandTotal  = [long]0
        $targetSizes = @()

        Write-Host "`n▶ SCANNING FOR CLEANABLE FILES..." -ForegroundColor Yellow
        Write-Host ("{0,-38} {1,-12} {2}" -f "TARGET", "SIZE", "FILES") -ForegroundColor Cyan
        Write-Host ("{0,-38} {1,-12} {2}" -f "──────", "────", "─────") -ForegroundColor DarkGray

        foreach ($t in $targets) {
            if (Test-Path $t.Path) {
                $filter = if ($t.Filter) { $t.Filter } else { "*" }
                $files = Get-ChildItem -Path $t.Path -Filter $filter -Recurse -File -Force -ErrorAction SilentlyContinue
                $sz    = ($files | Measure-Object -Property Length -Sum).Sum
                if (-not $sz) { $sz = 0 }
                $grandTotal += $sz
                $humanSz = Get-HumanSize -Bytes $sz
                Write-Host ("{0,-38} {1,-12} {2}" -f $t.Label, $humanSz, $files.Count) -ForegroundColor White
                $targetSizes += @{ Label=$t.Label; Path=$t.Path; Filter=$filter; Size=$sz; Count=$files.Count }
            } else {
                Write-Host ("{0,-38} {1,-12} {2}" -f $t.Label, "N/A", "—") -ForegroundColor DarkGray
            }
        }

        Write-Host ""
        Write-Host "   TOTAL RECOVERABLE: $(Get-HumanSize -Bytes $grandTotal)" -ForegroundColor Yellow

        if ($Mode -eq "SCAN" -or $DryRun) {
            Write-Host "`n   ℹ️  Scan complete. Run with Mode=CLEAN to actually delete." -ForegroundColor Cyan
            return
        }

        # ── Confirmation ────────────────────────────────────────────
        if (-not $SkipConfirm) {
            Write-Host ""
            Write-Host "   ⚠️  Delete $(Get-HumanSize -Bytes $grandTotal) of cached/temp/trash files?" -ForegroundColor Red
            Write-Host "   Type YES to confirm: " -ForegroundColor Yellow -NoNewline
            $answer = Read-Host
            if ($answer -ne "YES") { Write-Host "`n   ❌ Cancelled. No files were deleted." -ForegroundColor Gray; return }
        }

        # ── Delete ──────────────────────────────────────────────────
        Write-Host ""
        $deletedBytes = [long]0
        $deletedCount = 0

        foreach ($t in $targetSizes) {
            if ($t.Size -eq 0) { continue }
            Write-Host "   🗑️  Cleaning: $($t.Label)..." -ForegroundColor Yellow
            $r = Remove-DirectoryContents -DirPath $t.Path
            $deletedBytes += $r.Freed
            $deletedCount += $r.Removed
            if ($r.Errors.Count -gt 0) {
                $r.Errors | Select-Object -First 2 | ForEach-Object {
                    Write-Host "   ⚠️  $_" -ForegroundColor Yellow
                }
            }
            Write-Host ("   ✅ Done — {0} items, {1}" -f $r.Removed, (Get-HumanSize -Bytes $r.Freed)) -ForegroundColor Green
        }

        Write-Host ""
        Write-Host "──────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
        Write-Host "   ✅ CLEAN COMPLETE" -ForegroundColor Green
        Write-Host "   Files deleted : $deletedCount" -ForegroundColor White
        Write-Host "   Space freed   : $(Get-HumanSize -Bytes $deletedBytes)" -ForegroundColor White
        Write-Host "──────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
        return
    }

    # ── DUPLICATE FINDER ────────────────────────────────────────────
    if ($Mode -eq "DUPES" -or $Mode -eq "DEL_DUPES") {

        $searchDir = if ($ScanPath -and (Test-Path $ScanPath)) { $ScanPath } else { $HOME }
        Write-Host "`n▶ SCANNING FOR DUPLICATES IN: $searchDir" -ForegroundColor Yellow
        Write-Host "   (Comparing by MD5 hash — this may take a moment...)" -ForegroundColor DarkGray

        $hashGroups = @{}
        $allFiles = Get-ChildItem -Path $searchDir -Recurse -File -Force -ErrorAction SilentlyContinue |
            Where-Object { $_.Length -gt 10KB }

        $scanned = 0
        foreach ($f in $allFiles) {
            try {
                $hash = (Get-FileHash -Path $f.FullName -Algorithm MD5 -ErrorAction Stop).Hash
                if (-not $hashGroups.ContainsKey($hash)) { $hashGroups[$hash] = @() }
                $hashGroups[$hash] += $f
            } catch { }
            $scanned++
        }

        $dupeGroups = $hashGroups.GetEnumerator() | Where-Object { $_.Value.Count -gt 1 }
        $dupeList   = @($dupeGroups)

        if ($dupeList.Count -eq 0) {
            Write-Host "`n   ✅ No duplicate files found in $searchDir" -ForegroundColor Green
            return
        }

        $totalWaste  = [long]0
        $totalDupes  = 0

        Write-Host "`n   Found $($dupeList.Count) duplicate group(s):`n" -ForegroundColor Yellow
        Write-Host ("{0,-60} {1,-12} {2}" -f "FILE","SIZE","HASH") -ForegroundColor Cyan
        Write-Host ("{0,-60} {1,-12} {2}" -f "────","────","────") -ForegroundColor DarkGray

        foreach ($grp in $dupeList) {
            $files = $grp.Value | Sort-Object FullName
            Write-Host "  ┌─ DUPLICATE GROUP ($($files.Count) copies) ─────────────────────────" -ForegroundColor Magenta
            $first = $true
            foreach ($f in $files) {
                $sz  = Get-HumanSize -Bytes $f.Length
                if ($first) {
                    $pfx = "  │ [KEEP]   "
                    $col = "Green"
                } else {
                    $pfx = "  │ [DUPE]   "
                    $col = "Red"
                    $totalWaste += $f.Length
                    $totalDupes++
                }
                $pathDisplay = if ($f.FullName.Length -gt 57) { "..." + $f.FullName.Substring($f.FullName.Length-57) } else { $f.FullName }
                Write-Host ("{0}{1,-57} {2,-12}" -f $pfx, $pathDisplay, $sz) -ForegroundColor $col
                $first = $false
            }
            Write-Host "  └──────────────────────────────────────────────────────────" -ForegroundColor DarkGray
        }

        Write-Host ""
        Write-Host "   Duplicate files  : $totalDupes" -ForegroundColor White
        Write-Host "   Wasted space     : $(Get-HumanSize -Bytes $totalWaste)" -ForegroundColor Yellow

        if ($Mode -eq "DUPES") {
            Write-Host "`n   ℹ️  Run Mode=DEL_DUPES to remove duplicates (keeps first copy)." -ForegroundColor Cyan
            return
        }

        # ── Delete duplicates ────────────────────────────────────────
        if (-not $SkipConfirm) {
            Write-Host ""
            Write-Host "   ⚠️  Delete $totalDupes duplicate files, freeing $(Get-HumanSize -Bytes $totalWaste)?" -ForegroundColor Red
            Write-Host "   The FIRST copy of each group will be KEPT. Type YES to confirm: " -ForegroundColor Yellow -NoNewline
            $answer = Read-Host
            if ($answer -ne "YES") { Write-Host "`n   ❌ Cancelled. No files were deleted." -ForegroundColor Gray; return }
        }

        $delCount = 0; $delBytes = [long]0
        foreach ($grp in $dupeList) {
            $files = $grp.Value | Sort-Object FullName
            $skip  = $true
            foreach ($f in $files) {
                if ($skip) { $skip = $false; continue }
                try {
                    $sz = $f.Length
                    Remove-Item -Path $f.FullName -Force -ErrorAction Stop
                    $delCount++; $delBytes += $sz
                    Write-Host "   🗑️  Deleted: $($f.FullName)" -ForegroundColor Red
                } catch { Write-Host "   ⚠️  Could not delete: $($f.FullName) — $_" -ForegroundColor Yellow }
            }
        }

        Write-Host ""
        Write-Host "──────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
        Write-Host "   ✅ DUPLICATES REMOVED" -ForegroundColor Green
        Write-Host "   Files deleted : $delCount" -ForegroundColor White
        Write-Host "   Space freed   : $(Get-HumanSize -Bytes $delBytes)" -ForegroundColor White
        Write-Host "──────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
    }
}

# ============================================
# MAIN EXECUTION — CLI MODE
# ============================================

if ($Feature -gt 0) {
    switch ($Feature) {
        1  { Show-SystemInfo }
        2  { Show-ProcessMonitor }
        3  { Show-RealtimeMonitor }
        4  { Show-NetworkInfo }
        5  { Show-Bandwidth }
        6  { Show-PortScan }
        7  { Show-ServiceManager }
        8  { Show-DiskAnalysis }
        9  { Show-CleanupTools }
        10 { Show-SecurityCheck }
        11 { Show-PackageUpdates }
        12 { Show-HardwareInfo }
        13 { Get-FileList      -Directory $Path }
        14 { Copy-ItemPS       -Source $Source -Destination $Destination }
        15 { Move-ItemPS       -Source $Source -Destination $Destination }
        16 { Find-FileByName   -SearchPattern $SearchPattern -StartPath $Path }
        17 { Invoke-FileOrganizer -TargetDirectory $(if ($Path) { $Path } else { "." }) }
        # Smart Cleaner sub-modes
        18 { Invoke-SmartCleaner -Mode "SCAN" }
        19 { Invoke-SmartCleaner -Mode "CLEAN" -SkipConfirm:$SkipConfirm }
        20 { Invoke-SmartCleaner -Mode "DUPES" -ScanPath $(if ($Path) { $Path } else { $HOME }) }
        21 { Invoke-SmartCleaner -Mode "DEL_DUPES" -ScanPath $(if ($Path) { $Path } else { $HOME }) -SkipConfirm:$SkipConfirm }
        # Empty trash ONLY (complete wipe: files + info + expunged)
        26 { Invoke-EmptyTrash -SkipConfirm:$SkipConfirm }
        # Storage tools
        22 { Get-USBDrives }
        23 { Create-BootableDrive -Device $Device -IsoPath $IsoPath }
        24 { Get-StorageDevices }
        25 { Format-Storage -Device $Device -Filesystem $Filesystem -Label $Label }
        default { Write-Host "Invalid feature number: $Feature" -ForegroundColor Red }
    }
    exit 0
}

# ============================================
# MAIN EXECUTION — INTERACTIVE MENU LOOP
# ============================================

do {
    Show-Menu
    $choice = Read-Host "`n👉 Select an option (0-18)"

    switch ($choice) {
        "1"  { Show-SystemInfo }
        "2"  { Show-ProcessMonitor }
        "3"  { Show-RealtimeMonitor }
        "4"  { Show-NetworkInfo }
        "5"  { Show-Bandwidth }
        "6"  { Show-PortScan }
        "7"  { Show-ServiceManager }
        "8"  { Show-DiskAnalysis }
        "9"  { Show-CleanupTools }
        "10" { Show-SecurityCheck }
        "11" { Show-PackageUpdates }
        "12" { Show-HardwareInfo }

        "13" {
            $dir = Read-Host "Enter directory path"
            Get-FileList -Directory $dir
        }

        "14" {
            Write-Host "`n=== BOOTABLE DRIVE CREATOR ===" -ForegroundColor Cyan
            Get-USBDrives
            $device = Read-Host "`nEnter device path (e.g., /dev/sdb)"
            $iso    = Read-Host "Enter ISO file path"
            Create-BootableDrive -Device $device -IsoPath $iso
        }

        "15" {
            Write-Host "`n=== STORAGE FORMATTER ===" -ForegroundColor Cyan
            Get-StorageDevices
            $device = Read-Host "`nEnter device path (e.g., /dev/sdb1)"
            $fs     = Read-Host "Enter filesystem (ext4/ntfs/fat32/exfat)"
            $label  = Read-Host "Enter volume label (optional)"
            Format-Storage -Device $device -Filesystem $fs -Label $label
        }

        "16" {
            Write-Host "`n=== FILE SEARCH ===" -ForegroundColor Cyan
            $pattern   = Read-Host "Enter filename pattern"
            $startPath = Read-Host "Enter starting directory (Enter = current)"
            if (-not $startPath) { $startPath = "." }
            Find-FileByName -SearchPattern $pattern -StartPath $startPath
        }

        "17" {
            Write-Host "`n=== AUTOMATED FILE ORGANIZER ===" -ForegroundColor Cyan
            $targetDir = Read-Host "Enter directory to organize (Enter = current)"
            if (-not $targetDir) { $targetDir = "." }
            Invoke-FileOrganizer -TargetDirectory $targetDir
        }

        "18" {
            Write-Host "`n=== SMART CLEANER ===" -ForegroundColor Cyan
            Write-Host "  1) Scan (preview only)"        -ForegroundColor White
            Write-Host "  2) Clean cache/temp/trash"     -ForegroundColor White
            Write-Host "  3) Empty trash (complete)"     -ForegroundColor White
            Write-Host "  4) Find duplicates"            -ForegroundColor White
            Write-Host "  5) Delete duplicates"          -ForegroundColor White
            $sub = Read-Host "Choose action (1-5)"
            switch ($sub) {
                "1" { Invoke-SmartCleaner -Mode "SCAN" }
                "2" { Invoke-SmartCleaner -Mode "CLEAN" }
                "3" { Invoke-EmptyTrash }
                "4" {
                    $p = Read-Host "Directory to scan for duplicates (Enter = home)"
                    if (-not $p) { $p = $HOME }
                    Invoke-SmartCleaner -Mode "DUPES" -ScanPath $p
                }
                "5" {
                    $p = Read-Host "Directory to scan for duplicates (Enter = home)"
                    if (-not $p) { $p = $HOME }
                    Invoke-SmartCleaner -Mode "DEL_DUPES" -ScanPath $p
                }
                default { Write-Host "Invalid sub-option" -ForegroundColor Red }
            }
        }

        "0" {
            Write-Host "`n👋 Exiting Kali SmartOps Manager..." -ForegroundColor Yellow
            Write-Host "Thank you for using the tool!" -ForegroundColor Green
            break
        }

        default {
            Write-Host "`n❌ Invalid option! Please choose 0-18" -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }

    if ($choice -ne "0") {
        Write-Host "`n─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
        Write-Host "Press Enter to continue..."
        Read-Host
    }

} while ($choice -ne "0")