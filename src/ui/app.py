"""
Real-Time Scheduling System - User Interface
A modern GUI for configuring and visualizing real-time task scheduling.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import sys
from dataclasses import dataclass
from typing import List, Optional
import json

# Import the visualization module
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# ==================== DATA CLASSES ====================

@dataclass
class PeriodicTask:
    """Periodic Task: P r e p [d]"""
    release_time: float = 0.0
    execution_time: float = 1.0
    period: float = 10.0
    deadline: Optional[float] = None  # If None, deadline = period

@dataclass
class AperiodicTask:
    """Aperiodic Task: A r e"""
    release_time: float = 0.0
    execution_time: float = 1.0

@dataclass
class SporadicTask:
    """Sporadic Task (Deadline constrained): D e p d"""
    execution_time: float = 1.0
    period: float = 10.0
    deadline: float = 10.0

# ==================== COLOR SCHEME ====================

class Colors:
    """Cyberpunk-inspired color scheme"""
    BG_DARK = "#0a0e14"
    BG_MEDIUM = "#1a1f2c"
    BG_LIGHT = "#242b3d"
    ACCENT_PRIMARY = "#00d4ff"
    ACCENT_SECONDARY = "#ff6b9d"
    ACCENT_TERTIARY = "#c3e88d"
    ACCENT_WARNING = "#ffcb6b"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#8b95a8"
    TEXT_MUTED = "#4a5568"
    BORDER = "#2d3748"
    SUCCESS = "#48bb78"
    ERROR = "#fc8181"
    
    # Task type colors
    PERIODIC = "#00d4ff"
    APERIODIC = "#c3e88d"
    SPORADIC = "#ff6b9d"
    SERVER = "#ffcb6b"

# ==================== CUSTOM WIDGETS ====================

class ModernButton(tk.Button):
    """Custom styled button"""
    def __init__(self, parent, text, command=None, style="primary", **kwargs):
        colors = {
            "primary": (Colors.ACCENT_PRIMARY, Colors.BG_DARK),
            "secondary": (Colors.ACCENT_SECONDARY, Colors.TEXT_PRIMARY),
            "success": (Colors.SUCCESS, Colors.BG_DARK),
            "warning": (Colors.ACCENT_WARNING, Colors.BG_DARK),
        }
        bg, fg = colors.get(style, colors["primary"])
        
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=Colors.BG_LIGHT,
            activeforeground=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=8,
            **kwargs
        )
        self.bind("<Enter>", lambda e: self.config(bg=Colors.BG_LIGHT))
        self.bind("<Leave>", lambda e: self.config(bg=bg))

class ModernEntry(tk.Entry):
    """Custom styled entry"""
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.ACCENT_PRIMARY,
            relief=tk.FLAT,
            font=("Consolas", 11),
            **kwargs
        )

class ModernLabel(tk.Label):
    """Custom styled label"""
    def __init__(self, parent, text, style="normal", **kwargs):
        colors = {
            "normal": (Colors.TEXT_PRIMARY, ("Segoe UI", 10)),
            "title": (Colors.ACCENT_PRIMARY, ("Segoe UI", 14, "bold")),
            "subtitle": (Colors.TEXT_SECONDARY, ("Segoe UI", 9)),
            "header": (Colors.TEXT_PRIMARY, ("Segoe UI", 12, "bold")),
        }
        fg, font = colors.get(style, colors["normal"])
        
        super().__init__(
            parent,
            text=text,
            bg=Colors.BG_MEDIUM,
            fg=fg,
            font=font,
            **kwargs
        )

# ==================== MAIN APPLICATION ====================

class RealTimeSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Real-Time Scheduling System")
        self.root.geometry("1400x900")
        self.root.configure(bg=Colors.BG_DARK)
        self.root.minsize(1200, 700)
        
        # Data storage
        self.periodic_tasks: List[PeriodicTask] = []
        self.aperiodic_tasks: List[AperiodicTask] = []
        self.sporadic_tasks: List[SporadicTask] = []
        
        # Selected algorithm and server
        self.selected_algorithm = tk.StringVar(value="RM")
        self.selected_server = tk.StringVar(value="Background")
        
        # Paths
        self.data_dir = os.path.abspath(os.path.join(script_dir, "../../data"))
        self.input_file = os.path.join(self.data_dir, "input.txt")
        self.output_file = os.path.join(self.data_dir, "output.txt")
        self.chart_file = os.path.join(self.data_dir, "schedule_chart.png")
        
        # Build UI
        self._setup_styles()
        self._create_layout()
        self._load_existing_input()
        
    def _setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Treeview style
        style.configure(
            "Custom.Treeview",
            background=Colors.BG_LIGHT,
            foreground=Colors.TEXT_PRIMARY,
            fieldbackground=Colors.BG_LIGHT,
            rowheight=30,
            font=("Consolas", 10)
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=Colors.BG_MEDIUM,
            foreground=Colors.ACCENT_PRIMARY,
            font=("Segoe UI", 10, "bold")
        )
        style.map("Custom.Treeview", background=[("selected", Colors.ACCENT_PRIMARY)])
        
        # Combobox style
        style.configure(
            "Custom.TCombobox",
            fieldbackground=Colors.BG_LIGHT,
            background=Colors.BG_LIGHT,
            foreground=Colors.TEXT_PRIMARY,
            arrowcolor=Colors.ACCENT_PRIMARY
        )
        
    def _create_layout(self):
        """Create main application layout"""
        # Main container
        self.main_frame = tk.Frame(self.root, bg=Colors.BG_DARK)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self._create_header()
        
        # Content area (left panel + right panel)
        content_frame = tk.Frame(self.main_frame, bg=Colors.BG_DARK)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left panel - Task Configuration
        self._create_left_panel(content_frame)
        
        # Right panel - Visualization
        self._create_right_panel(content_frame)
        
    def _create_header(self):
        """Create header section"""
        header_frame = tk.Frame(self.main_frame, bg=Colors.BG_MEDIUM, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title with icon
        title_frame = tk.Frame(header_frame, bg=Colors.BG_MEDIUM)
        title_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        title_label = tk.Label(
            title_frame,
            text="⚡ REAL-TIME SCHEDULING SYSTEM",
            bg=Colors.BG_MEDIUM,
            fg=Colors.ACCENT_PRIMARY,
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(anchor="w")
        
        subtitle_label = tk.Label(
            title_frame,
            text="Configure, simulate, and visualize real-time task scheduling",
            bg=Colors.BG_MEDIUM,
            fg=Colors.TEXT_SECONDARY,
            font=("Segoe UI", 10)
        )
        subtitle_label.pack(anchor="w")
        
        # Action buttons
        action_frame = tk.Frame(header_frame, bg=Colors.BG_MEDIUM)
        action_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        run_btn = ModernButton(action_frame, "▶ RUN SCHEDULER", self._run_scheduler, style="success")
        run_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = ModernButton(action_frame, "💾 SAVE CONFIG", self._save_config, style="primary")
        save_btn.pack(side=tk.LEFT, padx=5)
        
        load_btn = ModernButton(action_frame, "📂 LOAD CONFIG", self._load_config, style="secondary")
        load_btn.pack(side=tk.LEFT, padx=5)
        
    def _create_left_panel(self, parent):
        """Create left panel with task configuration"""
        left_frame = tk.Frame(parent, bg=Colors.BG_MEDIUM, width=550)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        left_frame.pack_propagate(False)
        
        # Algorithm & Server Selection
        self._create_config_section(left_frame)
        
        # Task Input Section
        self._create_task_input_section(left_frame)
        
        # Task List Section
        self._create_task_list_section(left_frame)
        
    def _create_config_section(self, parent):
        """Create algorithm and server configuration section"""
        config_frame = tk.Frame(parent, bg=Colors.BG_MEDIUM)
        config_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Section title
        title = tk.Label(
            config_frame,
            text="⚙️ CONFIGURATION",
            bg=Colors.BG_MEDIUM,
            fg=Colors.ACCENT_PRIMARY,
            font=("Segoe UI", 12, "bold")
        )
        title.pack(anchor="w", pady=(0, 10))
        
        # Two-column layout
        columns_frame = tk.Frame(config_frame, bg=Colors.BG_MEDIUM)
        columns_frame.pack(fill=tk.X)
        
        # Algorithm selection
        algo_frame = tk.Frame(columns_frame, bg=Colors.BG_MEDIUM)
        algo_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        algo_label = tk.Label(
            algo_frame,
            text="Scheduling Algorithm",
            bg=Colors.BG_MEDIUM,
            fg=Colors.TEXT_SECONDARY,
            font=("Segoe UI", 9)
        )
        algo_label.pack(anchor="w")
        
        algorithms = [
            ("RM", "Rate Monotonic"),
            ("DM", "Deadline Monotonic"),
            ("EDF", "Earliest Deadline First"),
            ("LST", "Least Slack Time")
        ]
        
        algo_combo = ttk.Combobox(
            algo_frame,
            textvariable=self.selected_algorithm,
            values=[f"{code} - {name}" for code, name in algorithms],
            state="readonly",
            style="Custom.TCombobox",
            font=("Segoe UI", 10)
        )
        algo_combo.set("RM - Rate Monotonic")
        algo_combo.pack(fill=tk.X, pady=(5, 0))
        algo_combo.bind("<<ComboboxSelected>>", self._on_algorithm_change)
        
        # Server selection
        server_frame = tk.Frame(columns_frame, bg=Colors.BG_MEDIUM)
        server_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        server_label = tk.Label(
            server_frame,
            text="Aperiodic Task Server",
            bg=Colors.BG_MEDIUM,
            fg=Colors.TEXT_SECONDARY,
            font=("Segoe UI", 9)
        )
        server_label.pack(anchor="w")
        
        servers = ["Background", "Polling Server", "Deferrable Server"]
        
        server_combo = ttk.Combobox(
            server_frame,
            textvariable=self.selected_server,
            values=servers,
            state="readonly",
            style="Custom.TCombobox",
            font=("Segoe UI", 10)
        )
        server_combo.set("Background")
        server_combo.pack(fill=tk.X, pady=(5, 0))
        
    def _create_task_input_section(self, parent):
        """Create task input section"""
        input_frame = tk.Frame(parent, bg=Colors.BG_MEDIUM)
        input_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Section title
        title = tk.Label(
            input_frame,
            text="➕ ADD TASK",
            bg=Colors.BG_MEDIUM,
            fg=Colors.ACCENT_PRIMARY,
            font=("Segoe UI", 12, "bold")
        )
        title.pack(anchor="w", pady=(0, 10))
        
        # Task type tabs
        tab_frame = tk.Frame(input_frame, bg=Colors.BG_MEDIUM)
        tab_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.task_type_var = tk.StringVar(value="Periodic")
        
        for i, task_type in enumerate(["Periodic", "Sporadic", "Aperiodic"]):
            color = [Colors.PERIODIC, Colors.SPORADIC, Colors.APERIODIC][i]
            rb = tk.Radiobutton(
                tab_frame,
                text=task_type,
                variable=self.task_type_var,
                value=task_type,
                bg=Colors.BG_MEDIUM,
                fg=color,
                selectcolor=Colors.BG_DARK,
                activebackground=Colors.BG_MEDIUM,
                activeforeground=color,
                font=("Segoe UI", 10, "bold"),
                indicatoron=False,
                padx=15,
                pady=5,
                relief=tk.FLAT,
                borderwidth=2,
                command=self._update_input_fields
            )
            rb.pack(side=tk.LEFT, padx=(0, 5))
        
        # Input fields container
        self.input_fields_frame = tk.Frame(input_frame, bg=Colors.BG_LIGHT)
        self.input_fields_frame.pack(fill=tk.X, pady=(5, 10))
        
        self._update_input_fields()
        
        # Add button
        add_btn = ModernButton(input_frame, "➕ ADD TASK", self._add_task, style="success")
        add_btn.pack(anchor="w")
        
    def _update_input_fields(self):
        """Update input fields based on selected task type"""
        # Clear existing fields
        for widget in self.input_fields_frame.winfo_children():
            widget.destroy()
            
        task_type = self.task_type_var.get()
        
        fields_config = {
            "Periodic": [
                ("Release Time (r)", "release", "0"),
                ("Execution Time (e)", "exec", "1"),
                ("Period (p)", "period", "10"),
                ("Deadline (d)", "deadline", "")
            ],
            "Sporadic": [
                ("Execution Time (e)", "exec", "1"),
                ("Period (p)", "period", "10"),
                ("Deadline (d)", "deadline", "10")
            ],
            "Aperiodic": [
                ("Release Time (r)", "release", "0"),
                ("Execution Time (e)", "exec", "1")
            ]
        }
        
        self.input_entries = {}
        fields = fields_config.get(task_type, [])
        
        for i, (label_text, field_name, default) in enumerate(fields):
            field_frame = tk.Frame(self.input_fields_frame, bg=Colors.BG_LIGHT)
            field_frame.pack(fill=tk.X, padx=10, pady=5)
            
            label = tk.Label(
                field_frame,
                text=label_text,
                bg=Colors.BG_LIGHT,
                fg=Colors.TEXT_SECONDARY,
                font=("Segoe UI", 9),
                width=18,
                anchor="w"
            )
            label.pack(side=tk.LEFT)
            
            entry = ModernEntry(field_frame, width=15)
            entry.insert(0, default)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            
            self.input_entries[field_name] = entry
            
        # Add placeholder hint for deadline
        if task_type == "Periodic":
            hint = tk.Label(
                self.input_fields_frame,
                text="💡 Leave deadline empty to use period as deadline",
                bg=Colors.BG_LIGHT,
                fg=Colors.TEXT_MUTED,
                font=("Segoe UI", 8)
            )
            hint.pack(anchor="w", padx=10, pady=(0, 5))
            
    def _create_task_list_section(self, parent):
        """Create task list section with treeview"""
        list_frame = tk.Frame(parent, bg=Colors.BG_MEDIUM)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Section title with task count
        title_frame = tk.Frame(list_frame, bg=Colors.BG_MEDIUM)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title = tk.Label(
            title_frame,
            text="📋 TASK LIST",
            bg=Colors.BG_MEDIUM,
            fg=Colors.ACCENT_PRIMARY,
            font=("Segoe UI", 12, "bold")
        )
        title.pack(side=tk.LEFT)
        
        self.task_count_label = tk.Label(
            title_frame,
            text="(0 tasks)",
            bg=Colors.BG_MEDIUM,
            fg=Colors.TEXT_SECONDARY,
            font=("Segoe UI", 10)
        )
        self.task_count_label.pack(side=tk.LEFT, padx=10)
        
        # Delete button
        delete_btn = ModernButton(title_frame, "🗑️ DELETE", self._delete_selected_task, style="secondary")
        delete_btn.pack(side=tk.RIGHT)
        
        clear_btn = ModernButton(title_frame, "🧹 CLEAR ALL", self._clear_all_tasks, style="warning")
        clear_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Treeview with scrollbar
        tree_container = tk.Frame(list_frame, bg=Colors.BG_LIGHT)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Type", "Release", "Exec", "Period", "Deadline")
        self.task_tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse"
        )
        
        # Configure columns
        col_widths = [40, 80, 70, 60, 70, 70]
        for col, width in zip(columns, col_widths):
            self.task_tree.heading(col, text=col)
            self.task_tree.column(col, width=width, anchor="center")
            
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def _create_right_panel(self, parent):
        """Create right panel with visualization"""
        right_frame = tk.Frame(parent, bg=Colors.BG_MEDIUM)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Section title
        title_frame = tk.Frame(right_frame, bg=Colors.BG_MEDIUM)
        title_frame.pack(fill=tk.X, padx=15, pady=15)
        
        title = tk.Label(
            title_frame,
            text="📊 GANTT CHART VISUALIZATION",
            bg=Colors.BG_MEDIUM,
            fg=Colors.ACCENT_PRIMARY,
            font=("Segoe UI", 12, "bold")
        )
        title.pack(side=tk.LEFT)
        
        refresh_btn = ModernButton(title_frame, "🔄 REFRESH", self._refresh_chart, style="primary")
        refresh_btn.pack(side=tk.RIGHT)
        
        export_btn = ModernButton(title_frame, "📤 EXPORT", self._export_chart, style="secondary")
        export_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Chart container
        self.chart_container = tk.Frame(right_frame, bg=Colors.BG_DARK)
        self.chart_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Placeholder or chart
        self._show_chart_placeholder()
        
        # Status bar
        self.status_frame = tk.Frame(right_frame, bg=Colors.BG_LIGHT, height=40)
        self.status_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Ready. Add tasks and run the scheduler.",
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT_SECONDARY,
            font=("Consolas", 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=10)
        
    def _show_chart_placeholder(self):
        """Show placeholder when no chart is available"""
        for widget in self.chart_container.winfo_children():
            widget.destroy()
            
        placeholder = tk.Frame(self.chart_container, bg=Colors.BG_DARK)
        placeholder.pack(fill=tk.BOTH, expand=True)
        
        icon_label = tk.Label(
            placeholder,
            text="📈",
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_MUTED,
            font=("Segoe UI", 48)
        )
        icon_label.pack(expand=True, pady=(50, 10))
        
        text_label = tk.Label(
            placeholder,
            text="No visualization available yet.\nAdd tasks and run the scheduler to generate a Gantt chart.",
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_MUTED,
            font=("Segoe UI", 11),
            justify=tk.CENTER
        )
        text_label.pack(pady=(0, 50))
        
    # ==================== TASK MANAGEMENT ====================
    
    def _add_task(self):
        """Add a new task"""
        task_type = self.task_type_var.get()
        
        try:
            if task_type == "Periodic":
                release = float(self.input_entries["release"].get() or 0)
                exec_time = float(self.input_entries["exec"].get())
                period = float(self.input_entries["period"].get())
                deadline_str = self.input_entries["deadline"].get().strip()
                deadline = float(deadline_str) if deadline_str else None
                
                if exec_time <= 0 or period <= 0:
                    raise ValueError("Execution time and period must be positive")
                    
                task = PeriodicTask(release, exec_time, period, deadline)
                self.periodic_tasks.append(task)
                
            elif task_type == "Sporadic":
                exec_time = float(self.input_entries["exec"].get())
                period = float(self.input_entries["period"].get())
                deadline = float(self.input_entries["deadline"].get())
                
                if exec_time <= 0 or period <= 0 or deadline <= 0:
                    raise ValueError("All values must be positive")
                    
                task = SporadicTask(exec_time, period, deadline)
                self.sporadic_tasks.append(task)
                
            elif task_type == "Aperiodic":
                release = float(self.input_entries["release"].get() or 0)
                exec_time = float(self.input_entries["exec"].get())
                
                if exec_time <= 0:
                    raise ValueError("Execution time must be positive")
                    
                task = AperiodicTask(release, exec_time)
                self.aperiodic_tasks.append(task)
                
            self._update_task_list()
            self._set_status(f"✅ {task_type} task added successfully!", Colors.SUCCESS)
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter valid numeric values.\n{str(e)}")
            
    def _delete_selected_task(self):
        """Delete the selected task"""
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a task to delete.")
            return
            
        item = self.task_tree.item(selected[0])
        task_id = int(item["values"][0])
        task_type = item["values"][1]
        
        # Find and remove the task
        if task_type == "Periodic":
            idx = task_id - 1
            if 0 <= idx < len(self.periodic_tasks):
                self.periodic_tasks.pop(idx)
        elif task_type == "Sporadic":
            idx = task_id - len(self.periodic_tasks) - 1
            if 0 <= idx < len(self.sporadic_tasks):
                self.sporadic_tasks.pop(idx)
        elif task_type == "Aperiodic":
            idx = task_id - len(self.periodic_tasks) - len(self.sporadic_tasks) - 1
            if 0 <= idx < len(self.aperiodic_tasks):
                self.aperiodic_tasks.pop(idx)
                
        self._update_task_list()
        self._set_status("🗑️ Task deleted.", Colors.TEXT_SECONDARY)
        
    def _clear_all_tasks(self):
        """Clear all tasks"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all tasks?"):
            self.periodic_tasks.clear()
            self.sporadic_tasks.clear()
            self.aperiodic_tasks.clear()
            self._update_task_list()
            self._set_status("🧹 All tasks cleared.", Colors.TEXT_SECONDARY)
            
    def _update_task_list(self):
        """Update the task list treeview"""
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
            
        task_id = 1
        
        # Add periodic tasks
        for task in self.periodic_tasks:
            deadline = task.deadline if task.deadline else task.period
            self.task_tree.insert("", "end", values=(
                task_id, "Periodic", task.release_time, task.execution_time, 
                task.period, deadline
            ), tags=("periodic",))
            task_id += 1
            
        # Add sporadic tasks
        for task in self.sporadic_tasks:
            self.task_tree.insert("", "end", values=(
                task_id, "Sporadic", 0, task.execution_time,
                task.period, task.deadline
            ), tags=("sporadic",))
            task_id += 1
            
        # Add aperiodic tasks
        for task in self.aperiodic_tasks:
            self.task_tree.insert("", "end", values=(
                task_id, "Aperiodic", task.release_time, task.execution_time,
                "-", "-"
            ), tags=("aperiodic",))
            task_id += 1
            
        # Configure tag colors
        self.task_tree.tag_configure("periodic", foreground=Colors.PERIODIC)
        self.task_tree.tag_configure("sporadic", foreground=Colors.SPORADIC)
        self.task_tree.tag_configure("aperiodic", foreground=Colors.APERIODIC)
        
        # Update count
        total = len(self.periodic_tasks) + len(self.sporadic_tasks) + len(self.aperiodic_tasks)
        self.task_count_label.config(text=f"({total} tasks)")
        
    # ==================== FILE OPERATIONS ====================
    
    def _save_config(self):
        """Save current configuration to input file"""
        try:
            # Build input file content
            lines = []
            
            # Add header comment
            lines.append("# Real-Time Scheduling Configuration")
            lines.append(f"# Generated by RT Scheduler UI")
            lines.append("")
            
            # Add periodic tasks
            for task in self.periodic_tasks:
                if task.deadline and task.deadline != task.period:
                    # P r e p d
                    lines.append(f"P {task.release_time} {task.execution_time} {task.period} {task.deadline}")
                elif task.release_time != 0:
                    # P r e p
                    lines.append(f"P {task.release_time} {task.execution_time} {task.period}")
                else:
                    # P e p
                    lines.append(f"P {task.execution_time} {task.period}")
                    
            # Add sporadic tasks
            for task in self.sporadic_tasks:
                # D e p d
                lines.append(f"D {task.execution_time} {task.period} {task.deadline}")
                
            # Add aperiodic tasks with server policy
            server = self.selected_server.get()
            server_tag = ""
            if server == "Polling Server":
                server_tag = "(Poller)"
            elif server == "Deferrable Server":
                server_tag = "(Deferrable)"
                
            for task in self.aperiodic_tasks:
                # A r e [server_tag]
                line = f"A {task.release_time} {task.execution_time}"
                if server_tag:
                    line += f" {server_tag}"
                lines.append(line)
                
            # Ensure data directory exists
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Write to file
            with open(self.input_file, 'w') as f:
                f.write('\n'.join(lines))
                
            self._set_status(f"💾 Configuration saved to {os.path.basename(self.input_file)}", Colors.SUCCESS)
            messagebox.showinfo("Saved", f"Configuration saved to:\n{self.input_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration:\n{str(e)}")
            
    def _load_config(self):
        """Load configuration from file"""
        filepath = filedialog.askopenfilename(
            title="Load Configuration",
            initialdir=self.data_dir,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filepath:
            self._load_input_file(filepath)
            
    def _load_existing_input(self):
        """Load existing input.txt if available"""
        if os.path.exists(self.input_file):
            self._load_input_file(self.input_file)
            
    def _load_input_file(self, filepath):
        """Parse and load input file"""
        try:
            self.periodic_tasks.clear()
            self.sporadic_tasks.clear()
            self.aperiodic_tasks.clear()
            
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                        
                    # Remove inline comments
                    if '#' in line:
                        line = line.split('#')[0].strip()
                        
                    parts = line.split()
                    if not parts:
                        continue
                        
                    task_type = parts[0]
                    numbers = []
                    
                    # Parse numbers
                    for part in parts[1:]:
                        try:
                            numbers.append(float(part))
                        except ValueError:
                            # Check for server tag
                            if "Poller" in part:
                                self.selected_server.set("Polling Server")
                            elif "Deferrable" in part:
                                self.selected_server.set("Deferrable Server")
                                
                    if task_type == 'P':
                        if len(numbers) == 2:
                            # e, p
                            self.periodic_tasks.append(PeriodicTask(0, numbers[0], numbers[1], None))
                        elif len(numbers) == 3:
                            # r, e, p
                            self.periodic_tasks.append(PeriodicTask(numbers[0], numbers[1], numbers[2], None))
                        elif len(numbers) >= 4:
                            # r, e, p, d
                            self.periodic_tasks.append(PeriodicTask(numbers[0], numbers[1], numbers[2], numbers[3]))
                            
                    elif task_type == 'D':
                        if len(numbers) >= 3:
                            # e, p, d
                            self.sporadic_tasks.append(SporadicTask(numbers[0], numbers[1], numbers[2]))
                            
                    elif task_type == 'A':
                        if len(numbers) >= 2:
                            # r, e
                            self.aperiodic_tasks.append(AperiodicTask(numbers[0], numbers[1]))
                            
            self._update_task_list()
            self._set_status(f"📂 Loaded configuration from {os.path.basename(filepath)}", Colors.SUCCESS)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
            
    # ==================== SCHEDULER OPERATIONS ====================
    
    def _on_algorithm_change(self, event):
        """Handle algorithm selection change"""
        selection = self.selected_algorithm.get()
        algo_code = selection.split(" - ")[0]
        self.selected_algorithm.set(algo_code)
        
    def _run_scheduler(self):
        """Run the C++ scheduler"""
        if not (self.periodic_tasks or self.sporadic_tasks or self.aperiodic_tasks):
            messagebox.showwarning("No Tasks", "Please add at least one task before running the scheduler.")
            return
            
        # Save configuration first
        self._save_config()
        
        self._set_status("⏳ Running scheduler...", Colors.ACCENT_WARNING)
        self.root.update()
        
        try:
            # Find the executable
            build_dir = os.path.abspath(os.path.join(script_dir, "../../build"))
            exe_paths = [
                os.path.join(build_dir, "rt_scheduler.exe"),
                os.path.join(build_dir, "Release", "rt_scheduler.exe"),
                os.path.join(build_dir, "Debug", "rt_scheduler.exe"),
                os.path.join(build_dir, "rt_scheduler"),
            ]
            
            exe_path = None
            for path in exe_paths:
                if os.path.exists(path):
                    exe_path = path
                    break
                    
            if not exe_path:
                # Try to build first
                self._set_status("⚠️ Executable not found. Building project...", Colors.ACCENT_WARNING)
                self.root.update()
                
                # Check if CMakeLists.txt exists
                cmake_file = os.path.abspath(os.path.join(script_dir, "../../CMakeLists.txt"))
                if os.path.exists(cmake_file):
                    os.makedirs(build_dir, exist_ok=True)
                    
                    # Run cmake and build
                    subprocess.run(["cmake", ".."], cwd=build_dir, check=True, capture_output=True)
                    subprocess.run(["cmake", "--build", "."], cwd=build_dir, check=True, capture_output=True)
                    
                    # Check again for executable
                    for path in exe_paths:
                        if os.path.exists(path):
                            exe_path = path
                            break
                            
            if not exe_path:
                raise FileNotFoundError("Could not find or build rt_scheduler executable")
                
            # Get algorithm choice
            algo_map = {"RM": "1", "DM": "2", "EDF": "3", "LST": "4"}
            algo_choice = algo_map.get(self.selected_algorithm.get().split(" - ")[0], "1")
            
            # Run the scheduler
            result = subprocess.run(
                [exe_path],
                input=algo_choice + "\n",
                cwd=build_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self._set_status(f"❌ Scheduler error: {result.stderr}", Colors.ERROR)
            else:
                self._set_status("✅ Scheduling complete! Generating chart...", Colors.SUCCESS)
                self.root.update()
                
                # Generate the chart
                self._refresh_chart()
                
        except subprocess.TimeoutExpired:
            self._set_status("❌ Scheduler timeout (>60s)", Colors.ERROR)
        except FileNotFoundError as e:
            self._set_status(f"❌ {str(e)}", Colors.ERROR)
            messagebox.showerror("Error", f"Scheduler executable not found.\n\nPlease build the C++ project first:\n1. Create build directory\n2. Run: cmake ..\n3. Run: cmake --build .")
        except Exception as e:
            self._set_status(f"❌ Error: {str(e)}", Colors.ERROR)
            messagebox.showerror("Error", f"Failed to run scheduler:\n{str(e)}")
            
    # ==================== VISUALIZATION ====================
    
    def _refresh_chart(self):
        """Refresh the Gantt chart visualization"""
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showwarning("Missing Dependency", "Matplotlib is required for visualization.\nInstall it with: pip install matplotlib")
            return
            
        if not os.path.exists(self.output_file):
            self._set_status("⚠️ No output file found. Run the scheduler first.", Colors.ACCENT_WARNING)
            return
            
        try:
            # Parse output data
            tasks, misses = self._parse_output_file()
            
            if not tasks:
                self._set_status("⚠️ No scheduling data found in output file.", Colors.ACCENT_WARNING)
                return
                
            # Clear container
            for widget in self.chart_container.winfo_children():
                widget.destroy()
                
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor(Colors.BG_DARK)
            ax.set_facecolor(Colors.BG_DARK)
            
            # Colors for different task types
            chart_colors = {
                "Periodic": "#00d4ff",
                "Server(Poller)": "#ffcb6b",
                "Server(Deferrable)": "#ffcb6b",
                "Aperiodic": "#c3e88d",
                "Background": "#b39ddb",
                "Unknown": "#4a5568",
                "Server": "#ffcb6b"
            }
            
            y_labels = []
            y_ticks = []
            seen_types = set()
            
            # Sort tasks
            sorted_ids = sorted(tasks.keys(), key=lambda x: int(x) if x != '999' else 999999)
            task_y_map = {}
            
            for i, task_id in enumerate(sorted_ids):
                data = tasks[task_id]
                desc = data["desc"]
                intervals = data["intervals"]
                seen_types.add(desc)
                
                color = chart_colors.get(desc, "#4a5568")
                if "Server" in desc:
                    color = chart_colors["Server"]
                    
                ax.broken_barh(intervals, (i * 10, 9), facecolors=color, edgecolor='white', linewidth=0.5)
                
                y_labels.append(f"{desc}\n(ID: {task_id})")
                y_ticks.append(i * 10 + 4.5)
                task_y_map[task_id] = i * 10 + 4.5
                
            # Plot misses
            for time, task_id in misses:
                if task_id in task_y_map:
                    y_pos = task_y_map[task_id]
                    ax.axvline(x=time, color='#fc8181', linestyle='--', linewidth=2, alpha=0.8)
                    ax.scatter([time], [y_pos], color='#fc8181', marker='x', s=100, zorder=10)
                    
            # Styling
            ax.set_ylim(0, len(tasks) * 10 + 10)
            
            max_run = max([i[0]+i[1] for t in tasks.values() for i in t["intervals"]]) if tasks else 0
            max_miss = max([m[0] for m in misses]) if misses else 0
            ax.set_xlim(0, max(max_run, max_miss) + 0.5)
            
            ax.set_xlabel('Time (seconds)', color=Colors.TEXT_PRIMARY, fontsize=10)
            ax.set_yticks(y_ticks)
            ax.set_yticklabels(y_labels, color=Colors.TEXT_PRIMARY, fontsize=9)
            ax.tick_params(colors=Colors.TEXT_SECONDARY)
            ax.grid(True, axis='x', linestyle='--', alpha=0.3, color=Colors.TEXT_MUTED)
            
            # Spines
            for spine in ax.spines.values():
                spine.set_color(Colors.BORDER)
                
            # Legend
            patches = []
            for desc_type in sorted(seen_types):
                c = chart_colors.get(desc_type, "#4a5568")
                if "Server" in desc_type:
                    c = chart_colors["Server"]
                patches.append(mpatches.Patch(color=c, label=desc_type))
                
            if misses:
                patches.append(mpatches.Patch(color='#fc8181', label='DEADLINE MISS'))
                
            legend = ax.legend(handles=patches, loc='upper right', facecolor=Colors.BG_MEDIUM, 
                             edgecolor=Colors.BORDER, fontsize=9)
            for text in legend.get_texts():
                text.set_color(Colors.TEXT_PRIMARY)
                
            # Server policy in title
            server = self.selected_server.get()
            ax.set_title(f'Real-Time Schedule Execution\nServer: {server}', 
                        color=Colors.ACCENT_PRIMARY, fontsize=12, fontweight='bold')
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self._set_status("✅ Chart updated successfully!", Colors.SUCCESS)
            
        except Exception as e:
            self._set_status(f"❌ Chart error: {str(e)}", Colors.ERROR)
            
    def _parse_output_file(self):
        """Parse the output.txt file"""
        tasks = {}
        misses = []
        
        with open(self.output_file, 'r') as f:
            lines = f.readlines()[2:]  # Skip header
            
            for line in lines:
                parts = line.strip().split('\t')
                if len(parts) < 5:
                    continue
                    
                try:
                    time = float(parts[0])
                    task_id = parts[2]
                    desc = parts[3]
                    event = parts[4]
                except (ValueError, IndexError):
                    continue
                    
                if event in ["Running", "ServerExec", "BackgroundRun", "ServerExec(DS)"]:
                    if task_id not in tasks:
                        tasks[task_id] = {"intervals": [], "desc": desc}
                        
                    if "Server" in desc and "Server" not in tasks[task_id]["desc"]:
                        tasks[task_id]["desc"] = desc
                        
                    current_intervals = tasks[task_id]["intervals"]
                    
                    if current_intervals:
                        start, dur = current_intervals[-1]
                        if abs((start + dur) - time) < 0.0001:
                            current_intervals.pop()
                            current_intervals.append((start, dur + 0.1))
                        else:
                            current_intervals.append((time, 0.1))
                    else:
                        current_intervals.append((time, 0.1))
                        
                elif event == "DEADLINE_MISS":
                    misses.append((time, task_id))
                    if task_id not in tasks:
                        tasks[task_id] = {"intervals": [], "desc": "Failed Task"}
                        
        return tasks, misses
        
    def _export_chart(self):
        """Export the chart to a file"""
        if not os.path.exists(self.output_file):
            messagebox.showwarning("No Data", "Run the scheduler first to generate data.")
            return
            
        filepath = filedialog.asksaveasfilename(
            title="Export Chart",
            initialdir=self.data_dir,
            initialfile="schedule_chart.png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                # Use the existing visualizer module
                import visualizer
                visualizer.OUTPUT_IMAGE = filepath
                
                tasks, misses = visualizer.parse_data(self.output_file)
                if tasks:
                    policy = self.selected_server.get()
                    visualizer.plot_gantt(tasks, misses, policy)
                    
                self._set_status(f"📤 Chart exported to {os.path.basename(filepath)}", Colors.SUCCESS)
                messagebox.showinfo("Exported", f"Chart exported to:\n{filepath}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export chart:\n{str(e)}")
                
    def _set_status(self, message, color=None):
        """Update status bar"""
        self.status_label.config(text=message, fg=color or Colors.TEXT_SECONDARY)
        
# ==================== MAIN ====================

def main():
    root = tk.Tk()
    
    # Set window icon (optional)
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
        
    app = RealTimeSchedulerApp(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()

