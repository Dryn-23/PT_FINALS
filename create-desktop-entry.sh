#!/bin/bash
cat > ~/.local/share/applications/kali-smartops.desktop << EOF
[Desktop Entry]
Name=Kali SmartOps Manager PRO
Comment=Advanced System Administration Tool
Exec=pwsh -File /path/to/KaliSmartOpsUI.ps1
Icon=utilities-system-monitor
Terminal=false
Type=Application
Categories=System;Monitor;
StartupNotify=true
EOF

echo "✅ Desktop entry created!"
echo "📍 Find it in your Applications menu"