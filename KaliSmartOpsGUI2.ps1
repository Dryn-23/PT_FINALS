#Requires -Version 5.1
Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName WindowsBase
Add-Type -AssemblyName System.Windows.Forms

[xml]$Xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Kali SmartOps Manager PRO" 
        Height="800" Width="1200"
        WindowStartupLocation="CenterScreen"
        ResizeMode="CanResize"
        Background="#1a1a1a"
        FontFamily="Segoe UI"
        Icon="https://img.icons8.com/fluency/48/000000/linux.png">
    
    <Window.Resources>
        <!-- Modern Dark Theme -->
        <SolidColorBrush x:Key="PrimaryBackground" Color="#1a1a1a"/>
        <SolidColorBrush x:Key="SecondaryBackground" Color="#2d2d30"/>
        <SolidColorBrush x:Key="CardBackground" Color="#3a3a3e"/>
        <SolidColorBrush x:Key="AccentColor" Color="#00d4aa"/>
        <SolidColorBrush x:Key="AccentHover" Color="#00e6b8"/>
        <SolidColorBrush x:Key="TextPrimary" Color="White"/>
        <SolidColorBrush x:Key="TextSecondary" Color="#b0b0b3"/>
        <SolidColorBrush x:Key="DangerColor" Color="#ff4757"/>
        <SolidColorBrush x:Key="WarningColor" Color="#ffa502"/>
        <SolidColorBrush x:Key="SuccessColor" Color="#2ed573"/>
        
        <!-- Button Styles -->
        <Style x:Key="ModernButton" TargetType="Button">
            <Setter Property="Background" Value="{StaticResource AccentColor}"/>
            <Setter Property="Foreground" Value="{StaticResource TextPrimary}"/>
            <Setter Property="BorderThickness" Value="0"/>
            <Setter Property="Padding" Value="16,8"/>
            <Setter Property="Margin" Value="4,0"/>
            <Setter Property="FontSize" Value="13"/>
            <Setter Property="FontWeight" Value="SemiBold"/>
            <Setter Property="Cursor" Value="Hand"/>
            <Setter Property="Template">
                <Setter.Value>
                    <ControlTemplate TargetType="Button">
                        <Border Background="{TemplateBinding Background}"
                                CornerRadius="8"
                                BorderThickness="{TemplateBinding BorderThickness}">
                            <ContentPresenter HorizontalAlignment="Center"
                                            VerticalAlignment="Center"/>
                        </Border>
                        <ControlTemplate.Triggers>
                            <Trigger Property="IsMouseOver" Value="True">
                                <Setter Property="Background" Value="{StaticResource AccentHover}"/>
                            </Trigger>
                            <Trigger Property="IsPressed" Value="True">
                                <Setter Property="Background" Value="#00b894"/>
                            </Trigger>
                        </ControlTemplate.Triggers>
                    </ControlTemplate>
                </Setter.Value>
            </Setter>
        </Style>
        
        <Style x:Key="DangerButton" TargetType="Button" BasedOn="{StaticResource ModernButton}">
            <Setter Property="Background" Value="{StaticResource DangerColor}"/>
        </Style>
        
        <Style x:Key="WarningButton" TargetType="Button" BasedOn="{StaticResource ModernButton}">
            <Setter Property="Background" Value="{StaticResource WarningColor}"/>
        </Style>
        
        <!-- Card Style -->
        <Style x:Key="Card" TargetType="Border">
            <Setter Property="Background" Value="{StaticResource CardBackground}"/>
            <Setter Property="CornerRadius" Value="12"/>
            <Setter Property="Padding" Value="20"/>
            <Setter Property="Margin" Value="10"/>
            <Setter Property="Effect">
                <Setter.Value>
                    <DropShadowEffect Color="Black" Direction="270" ShadowDepth="5" BlurRadius="15" Opacity="0.3"/>
                </Setter.Value>
            </Setter>
        </Style>
        
        <!-- ScrollViewer Style -->
        <Style TargetType="ScrollViewer">
            <Setter Property="VerticalScrollBarVisibility" Value="Auto"/>
            <Setter Property="HorizontalScrollBarVisibility" Value="Disabled"/>
            <Setter Property="PanningMode" Value="VerticalOnly"/>
        </Style>
    </Window.Resources>
    
    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="60"/>
            <RowDefinition Height="*"/>
        </Grid.RowDefinitions>
        
        <!-- Header -->
        <Border Grid.Row="0" Background="#0f0f0f" BorderBrush="#404040" BorderThickness="0,0,0,1">
            <Grid>
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="Auto"/>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="Auto"/>
                </Grid.ColumnDefinitions>
                
                <TextBlock Grid.Column="0" 
                          Text="🛡️ KALI SMARTOPS MANAGER PRO" 
                          FontSize="24" 
                          FontWeight="Bold" 
                          Foreground="{StaticResource AccentColor}"
                          VerticalAlignment="Center"
                          Margin="20,0,0,0"/>
                
                <TextBlock Grid.Column="1" 
                          Text="Professional System Administration Tool" 
                          FontSize="14" 
                          Foreground="{StaticResource TextSecondary}"
                          VerticalAlignment="Center"
                          HorizontalAlignment="Center"/>
                
                <StackPanel Grid.Column="2" Orientation="Horizontal" VerticalAlignment="Center" Margin="0,0,20,0">
                    <Button Name="BtnRefresh" Content="🔄 Refresh" Style="{StaticResource ModernButton}" Click="BtnRefresh_Click"/>
                    <Button Name="BtnAbout" Content="ℹ️ About" Style="{StaticResource ModernButton}" Click="BtnAbout_Click" Margin="4,0,0,0"/>
                </StackPanel>
            </Grid>
        </Border>
        
        <!-- Main Content -->
        <Grid Grid.Row="1">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="280"/>
                <ColumnDefinition Width="*"/>
            </Grid.ColumnDefinitions>
            
            <!-- Sidebar Menu -->
            <Border Grid.Column="0" Background="{StaticResource SecondaryBackground}" BorderThickness="0,0,1,0">
                <ScrollViewer>
                    <StackPanel Margin="20">
                        <TextBlock Text="📋 QUICK ACTIONS" FontSize="14" FontWeight="SemiBold" 
                                  Foreground="{StaticResource AccentColor}" Margin="0,0,0,20"/>
                        
                        <Button Name="BtnSystemInfo" Content="📊 System Information" Style="{StaticResource ModernButton}" 
                               Click="BtnSystemInfo_Click" Height="50"/>
                        <Button Name="BtnProcesses" Content="🔍 Process Monitor" Style="{StaticResource ModernButton}" 
                               Click="BtnProcesses_Click" Height="50"/>
                        <Button Name="BtnRealtime" Content="📈 Real-time Monitor" Style="{StaticResource ModernButton}" 
                               Click="BtnRealtime_Click" Height="50"/>
                        <Button Name="BtnNetwork" Content="🌐 Network Info" Style="{StaticResource ModernButton}" 
                               Click="BtnNetwork_Click" Height="50"/>
                        <Button Name="BtnPorts" Content="🔌 Port Scanner" Style="{StaticResource ModernButton}" 
                               Click="BtnPorts_Click" Height="50"/>
                        <Button Name="BtnServices" Content="🔄 Services" Style="{StaticResource ModernButton}" 
                               Click="BtnServices_Click" Height="50"/>
                        <Button Name="BtnDisk" Content="💾 Disk Analysis" Style="{StaticResource ModernButton}" 
                               Click="BtnDisk_Click" Height="50"/>
                        <Button Name="BtnCleanup" Content="🧹 Cleanup Tools" Style="{StaticResource ModernButton}" 
                               Click="BtnCleanup_Click" Height="50"/>
                        <Button Name="BtnSecurity" Content="🔐 Security Check" Style="{StaticResource ModernButton}" 
                               Click="BtnSecurity_Click" Height="50"/>
                        <Button Name="BtnPackages" Content="📦 Updates" Style="{StaticResource ModernButton}" 
                               Click="BtnPackages_Click" Height="50"/>
                        <Button Name="BtnHardware" Content="🖥️ Hardware Info" Style="{StaticResource ModernButton}" 
                               Click="BtnHardware_Click" Height="50"/>
                        
                        <TextBlock Text="💻 FILE OPERATIONS" FontSize="14" FontWeight="SemiBold" 
                                  Foreground="{StaticResource AccentColor}" Margin="0,30,0,20"/>
                        
                        <Button Name="BtnFileManager" Content="📁 File Manager" Style="{StaticResource ModernButton}" 
                               Click="BtnFileManager_Click" Height="50"/>
                        <Button Name="BtnSearchFiles" Content="🔍 File Search" Style="{StaticResource ModernButton}" 
                               Click="BtnSearchFiles_Click" Height="50"/>
                        
                        <TextBlock Text="💿 STORAGE TOOLS" FontSize="14" FontWeight="SemiBold" 
                                  Foreground="{StaticResource AccentColor}" Margin="0,30,0,20"/>
                        
                        <Button Name="BtnUSBDrives" Content="💾 USB Drives" Style="{StaticResource ModernButton}" 
                               Click="BtnUSBDrives_Click" Height="50"/>
                        <Button Name="BtnStorage" Content="📀 Format Drive" Style="{StaticResource DangerButton}" 
                               Click="BtnStorage_Click" Height="50"/>
                    </StackPanel>
                </ScrollViewer>
            </Border>
            
            <!-- Content Area -->
            <Border Grid.Column="1" Background="{StaticResource PrimaryBackground}">
                <Grid>
                    <Grid.RowDefinitions>
                        <RowDefinition Height="Auto"/>
                        <RowDefinition Height="*"/>
                    </Grid.RowDefinitions>
                    
                    <!-- Content Title -->
                    <Border Grid.Row="0" Background="{StaticResource SecondaryBackground}" Padding="20" Margin="0,0,0,10">
                        <TextBlock Name="ContentTitle" 
                                  Text="Welcome to Kali SmartOps Manager PRO"
                                  FontSize="22" 
                                  FontWeight="Bold" 
                                  Foreground="{StaticResource TextPrimary}"/>
                    </Border>
                    
                    <!-- Content ScrollViewer -->
                    <ScrollViewer Grid.Row="1" Margin="20" Name="ContentScrollViewer">
                        <Border Name="ContentCard" Style="{StaticResource Card}">
                            <StackPanel Name="ContentPanel">
                                <TextBlock Text="Select a tool from the sidebar to get started!" 
                                          FontSize="16" 
                                          Foreground="{StaticResource TextSecondary}"
                                          HorizontalAlignment="Center"
                                          Margin="0,40,0,0"/>
                                <TextBlock Text="🎉 Professional system administration made easy!" 
                                          FontSize="14" 
                                          Foreground="{StaticResource TextSecondary}"
                                          HorizontalAlignment="Center"
                                          Margin="0,10,0,0"/>
                            </StackPanel>
                        </Border>
                    </ScrollViewer>
                </Grid>
            </Border>
        </Grid>
    </Grid>
</Window>
"@

# Create Window
$reader = (New-Object System.Xml.XmlNodeReader $Xaml)
$Window = [Windows.Markup.XamlReader]::Load($reader)

# Event Handlers
$Window | Add-Member -Type NoteProperty -Name "ScriptBlock" -Value $ExecutionContext.InvokeCommand.GetCommand('scriptblock::Invoke', 'All')

# Global Variables
$script:LastUpdateTime = Get-Date

# Function to Update Content
function Update-Content {
    param([string]$Title, [scriptblock]$ContentScript)
    
    $Window.FindName("ContentTitle").Text = $Title
    $contentPanel = $Window.FindName("ContentPanel")
    $contentPanel.Clear()
    
    try {
        $output = & $ContentScript
        $contentPanel.Add($output)
    }
    catch {
        $errorText = New-Object System.Windows.Controls.TextBlock
        $errorText.Text = "Error: $_"
        $errorText.Foreground = $Window.FindResource("DangerColor")
        $errorText.FontSize = 14
        $errorText.TextWrapping = "Wrap"
        $contentPanel.Add($errorText)
    }
}

# System Information Function
function Show-SystemInfo-GUI {
    Update-Content "📊 System Information" {
        $grid = New-Object System.Windows.Controls.Grid
        $grid.RowDefinitions.Add((New-Object System.Windows.Controls.RowDefinition -Property @{Height="Auto"}))
        
        $header = New-Object System.Windows.Controls.TextBlock
        $header.Text = "System Overview"
        $header.FontSize = 20
        $header.FontWeight = "Bold"
        $header.Foreground = $Window.FindResource("AccentColor")
        $header.Margin = "0,0,0,20"
        [System.Windows.Controls.Grid]::SetRow($header, 0)
        $grid.Children.Add($header)
        
        $osInfo = & lsb_release -d 2>$null | ForEach-Object { ($_ -split ':')[1].Trim() }
        if (-not $osInfo) {
            $osInfo = & grep PRETTY_NAME /etc/os-release 2>$null | cut -d'"' -f2
        }
        
        $infoGrid = New-Object System.Windows.Controls.Grid
        $infoGrid.ColumnDefinitions.Add((New-Object System.Windows.Controls.ColumnDefinition -Property @{Width="Auto"}))
        $infoGrid.ColumnDefinitions.Add((New-Object System.Windows.Controls.ColumnDefinition -Property @{Width="*"}))
        
        $labels = @("🖥️ OS", "⚙️ Kernel", "⏱️ Uptime", "🧠 CPU", "💾 Memory", "📊 Disk")
        $values = @(
            $osInfo,
            (& uname -r 2>$null),
            (& uptime -p 2>$null),
            (& lscpu 2>$null | grep "Model name" | cut -d':' -f2 | sed 's/^[ \t]*//'),
            (& free -h | grep Mem),
            (& df -h / | tail -1)
        )
        
        for ($i = 0; $i -lt $labels.Length; $i++) {
            $label = New-Object System.Windows.Controls.TextBlock
            $label.Text = $labels[$i]
            $label.FontWeight = "SemiBold"
            $label.Foreground = $Window.FindResource("TextPrimary")
            $label.VerticalAlignment = "Center"
            [System.Windows.Controls.Grid]::SetColumn($label, 0)
            [System.Windows.Controls.Grid]::SetRow($label, $i)
            $infoGrid.Children.Add($label)
            
            $value = New-Object System.Windows.Controls.TextBlock
            $value.Text = if ($values[$i]) { $values[$i] } else { "N/A" }
            $value.Foreground = $Window.FindResource("TextSecondary")
            $value.TextWrapping = "Wrap"
            $value.Margin = "15,0,0,10"
            [System.Windows.Controls.Grid]::SetColumn($value, 1)
            [System.Windows.Controls.Grid]::SetRow($value, $i)
            $infoGrid.Children.Add($value)
        }
        
        [System.Windows.Controls.Grid]::SetRow($infoGrid, 1)
        $grid.Children.Add($infoGrid)
        $grid
    }
}

# Process Monitor Function
function Show-Processes-GUI {
    Update-Content "🔍 Process Monitor (Top 15)" {
        $processes = & ps -eo pid,comm,%cpu,%mem --sort=-%cpu 2>$null | Select-Object -Skip 1 | Select-Object -First 15
        
        $header = New-Object System.Windows.Controls.TextBlock
        $header.Text = "Top Processes by CPU Usage"
        $header.FontSize = 20
        $header.FontWeight = "Bold"
        $header.Foreground = $Window.FindResource("AccentColor")
        $header.Margin = "0,0,0,20"
        
        $dataGrid = New-Object System.Windows.Controls.DataGrid
        $dataGrid.IsReadOnly = $true
        $dataGrid.AutoGenerateColumns = $false
        $dataGrid.Background = $Window.FindResource("CardBackground")
        $dataGrid.Foreground = $Window.FindResource("TextPrimary")
        $dataGrid.GridLinesVisibility = "None"
        $dataGrid.HeadersVisibility = "Column"
        $dataGrid.RowBackground = $Window.FindResource("SecondaryBackground")
        $dataGrid.AlternatingRowBackground = [System.Windows.Media.Brush]::Transparent
        
        $pidCol = New-Object System.Windows.Controls.DataGridTextColumn
        $pidCol.Header = "PID"
        $pidCol.Binding = New-Object System.Windows.Data.Binding "PID"
        $pidCol.Width = 80
        
        $nameCol = New-Object System.Windows.Controls.DataGridTextColumn
        $nameCol.Header = "Process"
        $nameCol.Binding = New-Object System.Windows.Data.Binding "Name"
        $nameCol.Width = 200
        
        $cpuCol = New-Object System.Windows.Controls.DataGridTextColumn
        $cpuCol.Header = "CPU%"
        $cpuCol.Binding = New-Object System.Windows.Data.Binding "CPU"
        $cpuCol.Width = 80
        
        $memCol = New-Object System.Windows.Controls.DataGridTextColumn
        $memCol.Header = "MEM%"
        $memCol.Binding = New-Object System.Windows.Data.Binding "Memory"
        $memCol.Width = 80
        
        $dataGrid.Columns.Add($pidCol)
        $dataGrid.Columns.Add($nameCol)
        $dataGrid.Columns.Add($cpuCol)
        $dataGrid.Columns.Add($memCol)
        
        foreach ($line in $processes) {
            $fields = $line -split '\s+' | Select-Object -First 4
            $item = New-Object PSObject -Property @{
                PID = $fields[0]
                Name = $fields[1]
                CPU = $fields[2]
                Memory = $fields[3]
            }
            $dataGrid.Items.Add($item)
        }
        
        $stack = New-Object System.Windows.Controls.StackPanel
        $stack.Children.Add($header)
        $stack.Children.Add($dataGrid)
        $stack
    }
}

# Event Handler Functions
$BtnSystemInfo_Click = {
    Show-SystemInfo-GUI
}

$BtnProcesses_Click = {
    Show-Processes-GUI
}

$BtnRealtime_Click = {
    Update-Content "📈 Real-time System Monitor" {

        $stack = New-Object System.Windows.Controls.StackPanel

        $title = New-Object System.Windows.Controls.TextBlock
        $title.Text = "Live System Metrics"
        $title.FontSize = 20
        $title.FontWeight = "Bold"
        $title.Foreground = $Window.FindResource("AccentColor")
        $title.Margin = "0,0,0,20"
        $stack.Children.Add($title)

        # CPU
        $cpu = (& top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}') 2>$null

        $cpuText = New-Object System.Windows.Controls.TextBlock
        $cpuText.Text = "CPU Usage: $cpu %"
        $cpuText.FontSize = 16
        $cpuText.Foreground = $Window.FindResource("TextPrimary")
        $stack.Children.Add($cpuText)

        # Memory
        $mem = (& free | grep Mem | awk '{print $3/$2 * 100.0}') 2>$null

        $memText = New-Object System.Windows.Controls.TextBlock
        $memText.Text = "Memory Usage: $([math]::Round($mem,2)) %"
        $memText.FontSize = 16
        $memText.Foreground = $Window.FindResource("TextPrimary")
        $memText.Margin = "0,10,0,0"
        $stack.Children.Add($memText)

        return $stack
    }
}

# Refresh Button
$BtnRefresh_Click = {
    Update-Content "🔄 Refreshed" {
        $text = New-Object System.Windows.Controls.TextBlock
        $text.Text = "✅ Data refreshed at $(Get-Date)"
        $text.Foreground = $Window.FindResource("SuccessColor")
        $text.FontSize = 16
        $text
    }
}

# About Button
$BtnAbout_Click = {
    Update-Content "ℹ️ About SmartOps" {
        $stack = New-Object System.Windows.Controls.StackPanel

        $title = New-Object System.Windows.Controls.TextBlock
        $title.Text = "Kali SmartOps Manager PRO"
        $title.FontSize = 20
        $title.FontWeight = "Bold"
        $title.Foreground = $Window.FindResource("AccentColor")

        $desc = New-Object System.Windows.Controls.TextBlock
        $desc.Text = "A professional Linux system monitoring and administration tool built using PowerShell + WPF.`n`nFeatures:`n• System Monitoring`n• Process Management`n• Network Tools`n• File Operations"
        $desc.TextWrapping = "Wrap"
        $desc.Margin = "0,10,0,0"
        $desc.Foreground = $Window.FindResource("TextSecondary")

        $stack.Children.Add($title)
        $stack.Children.Add($desc)

        return $stack
    }
}

$timer = New-Object System.Windows.Threading.DispatcherTimer
$timer.Interval = [TimeSpan]::FromSeconds(2)

$timer.Add_Tick({
    # Auto update only if Realtime is open
    if ($Window.FindName("ContentTitle").Text -like "*Real-time*") {
        & $BtnRealtime_Click
    }
})

$timer.Start()

# Connect buttons to functions
$Window.FindName("BtnRefresh").Add_Click($BtnRefresh_Click)
$Window.FindName("BtnAbout").Add_Click($BtnAbout_Click)
$Window.FindName("BtnSystemInfo").Add_Click($BtnSystemInfo_Click)
$Window.FindName("BtnProcesses").Add_Click($BtnProcesses_Click)
$Window.FindName("BtnRealtime").Add_Click($BtnRealtime_Click)

function NotImplemented($name) {
    Update-Content "$name" {
        $text = New-Object System.Windows.Controls.TextBlock
        $text.Text = "⚠️ Feature not implemented yet."
        $text.Foreground = $Window.FindResource("WarningColor")
        $text.FontSize = 16
        $text
    }
}

$Window.FindName("BtnNetwork").Add_Click({ NotImplemented "Network Info" })
$Window.FindName("BtnPorts").Add_Click({ NotImplemented "Port Scanner" })
$Window.FindName("BtnServices").Add_Click({ NotImplemented "Services" })
$Window.FindName("BtnDisk").Add_Click({ NotImplemented "Disk Analysis" })
$Window.FindName("BtnCleanup").Add_Click({ NotImplemented "Cleanup Tools" })
$Window.FindName("BtnSecurity").Add_Click({ NotImplemented "Security Check" })
$Window.FindName("BtnPackages").Add_Click({ NotImplemented "Updates" })
$Window.FindName("BtnHardware").Add_Click({ NotImplemented "Hardware Info" })
$Window.FindName("BtnFileManager").Add_Click({ NotImplemented "File Manager" })
$Window.FindName("BtnSearchFiles").Add_Click({ NotImplemented "File Search" })
$Window.FindName("BtnUSBDrives").Add_Click({ NotImplemented "USB Drives" })
$Window.FindName("BtnStorage").Add_Click({ NotImplemented "Format Drive" })

# Show Window
$Window.ShowDialog() | Out-Null
