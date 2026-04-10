import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import os

class SmartOpsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Kali SmartOps Manager PRO")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(True, True)
        
        # Center window
        self.center_window()
        
        # Variables for file operations
        self.current_path = tk.StringVar(value=os.getcwd())
        self.search_pattern = tk.StringVar()
        self.source_path = tk.StringVar()
        self.dest_path = tk.StringVar()
        self.device_path = tk.StringVar()
        self.iso_path = tk.StringVar()
        self.filesystem = tk.StringVar(value="ext4")
        self.label = tk.StringVar()
        
        self.create_widgets()
        
    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
    
    def create_widgets(self):
        # Title
        title_frame = tk.Frame(self.root, bg="#1e1e1e")
        title_frame.pack(fill="x", pady=(10, 20))
        
        title = tk.Label(title_frame, 
                        text="🛠️  KALI SMARTOPS MANAGER PRO", 
                        bg="#1e1e1e", fg="#00ff88", 
                        font=("Arial", 20, "bold"))
        title.pack()
        
        subtitle = tk.Label(title_frame, 
                          text="Advanced System Administration & Management Tool", 
                          bg="#1e1e1e", fg="#888", 
                          font=("Arial", 12))
        subtitle.pack(pady=(5, 0))
        
        # Main container
        main_container = tk.Frame(self.root, bg="#1e1e1e")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left sidebar - Main features
        self.sidebar = tk.Frame(main_container, bg="#2d2d30", width=280)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        # Right side - Output + Controls
        right_frame = tk.Frame(main_container, bg="#1e1e1e")
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Output area
        output_frame = tk.Frame(right_frame, bg="#1e1e1e")
        output_frame.pack(fill="both", expand=True)
        
        tk.Label(output_frame, text="📊 OUTPUT", bg="#1e1e1e", fg="#00ff88",
                font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, wrap="word", bg="#0d1117", fg="#c9d1d9",
            font=("Consolas", 11), insertbackground="white",
            selectbackground="#238636", padx=10, pady=10
        )
        self.output_text.pack(fill="both", expand=True)
        
        # Control panel (bottom)
        self.control_frame = tk.Frame(right_frame, bg="#161b22", height=200)
        self.control_frame.pack(fill="x", pady=(10, 0))
        self.control_frame.pack_propagate(False)
        
        self.create_sidebar_buttons()
        self.create_control_panel()
        
    def create_sidebar_buttons(self):
        # Button style
        button_style = {
            "bg": "#21262d",
            "fg": "white",
            "activebackground": "#238636",
            "activeforeground": "white",
            "relief": "flat",
            "font": ("Segoe UI", 10, "bold"),
            "pady": 12,
            "padx": 15,
            "anchor": "w",
            "borderwidth": 0,
            "cursor": "hand2"
        }
        
        # Button categories
        categories = [
            ("📊 System Monitoring", [
                ("System Info", 1),
                ("Process Monitor", 2),
                ("Realtime Monitor", 3),
                ("Network Info", 4),
                ("Bandwidth Usage", 5),
            ]),
            ("🔒 Security & Services", [
                ("Port Scan", 6),
                ("Service Manager", 7),
                ("Security Check", 10),
            ]),
            ("💾 Storage & Disk", [
                ("Disk Usage", 8),
                ("Hardware Info", 12),
                ("Storage Devices", 22),
            ]),
            ("🧹 Maintenance", [
                ("System Cleanup", 9),
                ("Package Updates", 11),
            ]),
            ("📁 File Operations", [
                ("File Manager", 13),
                ("File Search", 16),
            ]),
            ("💿 Advanced Tools", [
                ("Bootable Drive", 20),
                ("Format Storage", 23),
            ])
        ]
        
        tk.Label(self.sidebar, text="MAIN FEATURES", bg="#2d2d30", fg="#00ff88",
                font=("Arial", 12, "bold")).pack(pady=(15, 10), anchor="w", padx=15)
        
        for category_name, buttons in categories:
            # Category label
            cat_label = tk.Label(self.sidebar, text=category_name, bg="#2d2d30", 
                               fg="#58a6ff", font=("Arial", 11, "bold"))
            cat_label.pack(anchor="w", padx=15, pady=(15, 5))
            
            # Category buttons
            for text, feature in buttons:
                btn = tk.Button(self.sidebar, text=text, command=lambda f=feature: self.run_feature(f),
                               **button_style)
                btn.pack(fill="x", padx=15, pady=2)
        
        # Clear output button
        clear_btn = tk.Button(self.sidebar, text="🗑️  Clear Output", 
                             command=self.clear_output,
                             bg="#da3633", fg="white",
                             activebackground="#f85149",
                             font=("Segoe UI", 10, "bold"),
                             pady=10, padx=15, relief="flat")
        clear_btn.pack(fill="x", padx=15, pady=(20, 15))
    
    def create_control_panel(self):
        # Control panel tabs
        notebook = ttk.Notebook(self.control_frame, style="Dark.TNotebook")
        notebook.pack(fill="both", expand=True, padx=15, pady=15)
        
        # File Operations tab
        file_tab = ttk.Frame(notebook)
        notebook.add(file_tab, text="📁 File Operations")
        self.create_file_controls(file_tab)
        
        # Storage tab
        storage_tab = ttk.Frame(notebook)
        notebook.add(storage_tab, text="💿 Storage Tools")
        self.create_storage_controls(storage_tab)
        
        # Search tab
        search_tab = ttk.Frame(notebook)
        notebook.add(search_tab, text="🔍 Search")
        self.create_search_controls(search_tab)
    
    def create_file_controls(self, parent):
        # Path selection
        path_frame = tk.Frame(parent, bg="#161b22")
        path_frame.pack(fill="x", pady=(10, 15))
        
        tk.Label(path_frame, text="Current Path:", bg="#161b22", fg="white",
                font=("Arial", 10, "bold")).pack(side="left")
        
        path_entry = tk.Entry(path_frame, textvariable=self.current_path, 
                             bg="#0d1117", fg="white", font=("Consolas", 10),
                             relief="flat", bd=1)
        path_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        
        tk.Button(path_frame, text="📂 Browse", 
                 command=lambda: self.browse_folder(self.current_path),
                 bg="#238636", fg="white", relief="flat",
                 font=("Arial", 10)).pack(side="right", padx=(0, 10))
        
        tk.Button(path_frame, text="📋 List Files", 
                 command=lambda: self.run_feature(13),
                 bg="#58a6ff", fg="white", relief="flat",
                 font=("Arial", 10)).pack(side="right")
        
        # File operations
        ops_frame = tk.Frame(parent, bg="#161b22")
        ops_frame.pack(fill="x")
        
        tk.Button(ops_frame, text="📤 Copy File/Folder", 
                 command=lambda: self.run_feature_with_paths(14),
                 bg="#dbab09", fg="white", relief="flat",
                 font=("Arial", 10), pady=8).pack(fill="x", pady=2)
        
        tk.Button(ops_frame, text="✂️  Move File/Folder", 
                 command=lambda: self.run_feature_with_paths(15),
                 bg="#dbab09", fg="white", relief="flat",
                 font=("Arial", 10), pady=8).pack(fill="x", pady=2)
    
    def create_storage_controls(self, parent):
        # Device selection
        device_frame = tk.Frame(parent, bg="#161b22")
        device_frame.pack(fill="x", pady=(10, 15))
        
        tk.Label(device_frame, text="⚠️  Target Device:", bg="#161b22", fg="#f85149",
                font=("Arial", 10, "bold")).pack(anchor="w")
        
        device_entry = tk.Entry(device_frame, textvariable=self.device_path,
                               bg="#0d1117", fg="white", font=("Consolas", 10),
                               relief="flat")
        device_entry.pack(fill="x", pady=(5, 10))
        
        tk.Button(device_frame, text="💾 List Devices", 
                 command=lambda: self.run_feature(22),
                 bg="#238636", fg="white", relief="flat",
                 font=("Arial", 10)).pack()
        
        # Bootable drive
        boot_frame = tk.LabelFrame(parent, text="💿 Create Bootable USB", 
                                  bg="#161b22", fg="#00ff88", font=("Arial", 11, "bold"))
        boot_frame.pack(fill="x", pady=(20, 10))
        
        tk.Button(boot_frame, text="📋 List USB Drives", 
                 command=lambda: self.run_feature(20),
                 bg="#58a6ff", fg="white").pack(pady=5)
        
        iso_frame = tk.Frame(boot_frame, bg="#161b22")
        iso_frame.pack(fill="x", pady=5)
        tk.Entry(iso_frame, textvariable=self.iso_path, bg="#0d1117", fg="white").pack(side="left", fill="x", expand=True, padx=(5, 5))
        tk.Button(iso_frame, text="📀 Browse ISO", command=lambda: self.browse_file(self.iso_path, "*.iso")).pack(side="right")
        
        tk.Button(boot_frame, text="🚀 CREATE BOOTABLE USB", 
                 command=lambda: self.run_feature(21),
                 bg="#da3633", fg="white", font=("Arial", 10, "bold")).pack(pady=10)
        
        # Format storage
        format_frame = tk.LabelFrame(parent, text="💾 Format Storage", 
                                    bg="#161b22", fg="#00ff88", font=("Arial", 11, "bold"))
        format_frame.pack(fill="x", pady=10)
        
        fs_frame = tk.Frame(format_frame, bg="#161b22")
        fs_frame.pack(fill="x")
        tk.Label(fs_frame, text="Filesystem:", bg="#161b22", fg="white").pack(side="left")
        fs_combo = ttk.Combobox(fs_frame, textvariable=self.filesystem, 
                               values=["ext4", "ntfs", "fat32", "exfat"],
                               state="readonly", width=10)
        fs_combo.pack(side="left", padx=(10, 5))
        
        tk.Entry(format_frame, textvariable=self.label, bg="#0d1117", fg="white").pack(fill="x", pady=5)
        tk.Button(format_frame, text="⚡ FORMAT DEVICE", 
                 command=lambda: self.run_feature(23),
                 bg="#da3633", fg="white", font=("Arial", 10, "bold")).pack(pady=10)
    
    def create_search_controls(self, parent):
        tk.Label(parent, text="🔍 File Search", bg="#161b22", fg="#00ff88",
                font=("Arial", 12, "bold")).pack(pady=(10, 5))
        
        pattern_frame = tk.Frame(parent, bg="#161b22")
        pattern_frame.pack(fill="x", pady=5)
        tk.Label(pattern_frame, text="Pattern:", bg="#161b22", fg="white").pack(side="left")
        tk.Entry(pattern_frame, textvariable=self.search_pattern, bg="#0d1117", fg="white").pack(side="left", fill="x", expand=True, padx=(10, 5))
        tk.Button(pattern_frame, text="🔍 SEARCH", command=lambda: self.run_feature(16),
                 bg="#238636", fg="white").pack(side="right", padx=5)
        
        path_frame = tk.Frame(parent, bg="#161b22")
        path_frame.pack(fill="x", pady=5)
        tk.Entry(path_frame, textvariable=self.current_path, bg="#0d1117", fg="white").pack(side="left", fill="x", expand=True)
        tk.Button(path_frame, text="📂 Browse", command=lambda: self.browse_folder(self.current_path),
                 bg="#58a6ff", fg="white").pack(side="right", padx=5)
    
    def browse_folder(self, var):
        folder = filedialog.askdirectory(initialdir=var.get())
        if folder:
            var.set(folder)
    
    def browse_file(self, var, filetypes):
        filename = filedialog.askopenfilename(filetypes=[("ISO files", "*.iso"), ("All files", "*.*")])
        if filename:
            var.set(filename)
    
    def run_feature(self, feature):
        """Run simple feature"""
        self.execute_command(f"pwsh smartops.ps1 -Feature {feature}")
    
    def run_feature_with_paths(self, feature):
        """Run feature with path parameters"""
        if feature == 14 or feature == 15:  # Copy/Move
            self.source_path.set(filedialog.askopenfilename())
            if self.source_path.get():
                self.dest_path.set(filedialog.askdirectory())
                if self.dest_path.get():
                    cmd = f"pwsh smartops.ps1 -Feature {feature} -Source '{self.source_path.get()}' -Destination '{self.dest_path.get()}'"
                    self.execute_command(cmd)
        else:
            self.run_feature(feature)
    
    def run_feature(self, feature):
        """Run feature with appropriate parameters"""
        cmd = f"pwsh smartops.ps1 -Feature {feature}"
        
        if feature == 16:  # File search
            if self.search_pattern.get():
                cmd += f" -SearchPattern '{self.search_pattern.get()}' -Path '{self.current_path.get()}'"
        
        elif feature in [14, 15]:  # Copy/Move
            self.prompt_paths(feature)
            return
        
        elif feature == 21:  # Bootable drive
            if self.device_path.get() and self.iso_path.get():
                cmd += f" -Device '{self.device_path.get()}' -IsoPath '{self.iso_path.get()}'"
            else:
                messagebox.showwarning("Missing Input", "Please set Device and ISO path!")
                return
        
        elif feature == 23:  # Format storage
            if self.device_path.get():
                cmd += f" -Device '{self.device_path.get()}' -Filesystem '{self.filesystem.get()}'"
                if self.label.get():
                    cmd += f" -Label '{self.label.get()}'"
            else:
                messagebox.showwarning("Missing Input", "Please set Device path!")
                return
        
        elif feature == 13:  # File list
            cmd += f" -Path '{self.current_path.get()}'"
        
        self.execute_command(cmd)
    
    def prompt_paths(self, feature):
        """Interactive path selection for copy/move"""
        if feature in [14, 15]:
            source = filedialog.askopenfilename(title="Select Source")
            if source:
                dest = filedialog.askdirectory(title="Select Destination")
                if dest:
                    cmd = f"pwsh smartops.ps1 -Feature {feature} -Source '{source}' -Destination '{dest}'"
                    self.execute_command(cmd)
    
    def execute_command(self, command):
        """Execute command in separate thread"""
        def run():
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"🔄 Executing: {command}\n\n")
            self.output_text.see(tk.END)
            
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
                self.output_text.insert(tk.END, result.stdout)
                if result.stderr:
                    self.output_text.insert(tk.END, f"\n{'='*60}\nERRORS:\n{result.stderr}")
            except subprocess.TimeoutExpired:
                self.output_text.insert(tk.END, "\n❌ Command timed out after 5 minutes!")
            except Exception as e:
                self.output_text.insert(tk.END, f"\n❌ Error: {str(e)}")
            
            self.output_text.see(tk.END)
        
        threading.Thread(target=run, daemon=True).start()
    
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)

def main():
    root = tk.Tk()
    app = SmartOpsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
