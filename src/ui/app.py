"""
Real-Time Scheduling System - Modern UI
Drag & Drop support, Budget tracking, Modern design
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import subprocess
import os
import sys

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../data"))
INPUT_FILE = os.path.join(DATA_DIR, "input.txt")
OUTPUT_FILE = os.path.join(DATA_DIR, "output.txt")
BUILD_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../build"))
EXE_PATH = os.path.join(BUILD_DIR, "rt_scheduler.exe")

# Try to import matplotlib
try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.patches as mpatches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Try to import tkinterdnd2 for drag and drop
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

# Color scheme
class Theme:
    BG = "#0f0f0f"
    BG2 = "#1a1a1a"
    BG3 = "#252525"
    ACCENT = "#00d4aa"
    ACCENT2 = "#7c3aed"
    TEXT = "#e4e4e7"
    TEXT2 = "#a1a1aa"
    TEXT3 = "#52525b"
    RED = "#ef4444"
    ORANGE = "#f97316"
    GREEN = "#22c55e"
    BLUE = "#3b82f6"
    PURPLE = "#a855f7"

class ModernSchedulerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Scheduler")
        self.root.geometry("1300x800")
        self.root.configure(bg=Theme.BG)
        self.root.minsize(1100, 700)
        
        self.algorithm = tk.StringVar(value="1")
        self.current_file = INPUT_FILE
        
        self._create_ui()
        self._load_input_file()
        self._setup_drag_drop()
        
    def _setup_drag_drop(self):
        """Setup drag and drop if available"""
        if HAS_DND:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self._on_drop)
        
    def _on_drop(self, event):
        """Handle dropped files"""
        file_path = event.data
        # Clean up path (remove curly braces if present)
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        
        if os.path.isfile(file_path) and file_path.endswith('.txt'):
            self._load_file(file_path)
            self._set_status(f"Loaded: {os.path.basename(file_path)}", Theme.GREEN)
        else:
            self._set_status("Invalid file. Please drop a .txt file", Theme.RED)
            
    def _create_ui(self):
        # Main container
        main = tk.Frame(self.root, bg=Theme.BG)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header
        self._create_header(main)
        
        # Content
        content = tk.Frame(main, bg=Theme.BG)
        content.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # Left panel
        self._create_left_panel(content)
        
        # Right panel
        self._create_right_panel(content)
        
        # Status bar
        self.status_frame = tk.Frame(self.root, bg=Theme.BG2, height=35)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_frame.pack_propagate(False)
        
        self.status = tk.Label(
            self.status_frame, text="Ready - Drag & drop input.txt or use Open button",
            bg=Theme.BG2, fg=Theme.TEXT2, font=("Segoe UI", 9), anchor="w", padx=15
        )
        self.status.pack(fill=tk.BOTH, expand=True, pady=8)
        
    def _create_header(self, parent):
        header = tk.Frame(parent, bg=Theme.BG2, height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Left side - Title
        left = tk.Frame(header, bg=Theme.BG2)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        title = tk.Label(left, text="RT SCHEDULER", bg=Theme.BG2, fg=Theme.ACCENT,
                        font=("Segoe UI", 18, "bold"))
        title.pack(anchor="w", pady=(12, 0))
        
        subtitle = tk.Label(left, text="Real-Time Task Scheduling Simulator",
                           bg=Theme.BG2, fg=Theme.TEXT2, font=("Segoe UI", 9))
        subtitle.pack(anchor="w")
        
        # Right side - Buttons
        right = tk.Frame(header, bg=Theme.BG2)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=15)
        
        self._create_button(right, "OPEN", self._open_file, Theme.BG3, Theme.TEXT).pack(side=tk.LEFT, padx=3)
        self._create_button(right, "SAVE", self._save_input, Theme.BLUE, "#fff").pack(side=tk.LEFT, padx=3)
        self._create_button(right, "RUN", self._run_scheduler, Theme.GREEN, "#fff").pack(side=tk.LEFT, padx=3)
        self._create_button(right, "CHART", self._show_chart, Theme.PURPLE, "#fff").pack(side=tk.LEFT, padx=3)
        
    def _create_button(self, parent, text, command, bg, fg):
        btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                       font=("Segoe UI", 10, "bold"), relief=tk.FLAT,
                       padx=18, pady=6, cursor="hand2", activebackground=Theme.BG3)
        btn.bind("<Enter>", lambda e: btn.config(bg=Theme.ACCENT if bg != Theme.BG3 else Theme.BG2))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn
        
    def _create_left_panel(self, parent):
        left = tk.Frame(parent, bg=Theme.BG2, width=450)
        left.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left.pack_propagate(False)
        
        # Drop zone / Editor
        drop_frame = tk.Frame(left, bg=Theme.BG2)
        drop_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title
        title_frame = tk.Frame(drop_frame, bg=Theme.BG2)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(title_frame, text="INPUT FILE", bg=Theme.BG2, fg=Theme.ACCENT,
                font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
        
        self.file_label = tk.Label(title_frame, text="input.txt", bg=Theme.BG2, 
                                   fg=Theme.TEXT3, font=("Segoe UI", 9))
        self.file_label.pack(side=tk.RIGHT)
        
        # Help text
        help_frame = tk.Frame(drop_frame, bg=Theme.BG3)
        help_frame.pack(fill=tk.X, pady=(0, 10))
        
        help_text = """P e p       → Periodic (deadline = period)
P r e p     → Periodic with release time
D e p d     → Periodic with explicit deadline
A r e       → Aperiodic task
A r e (Poller/Deferrable) → With server"""
        
        tk.Label(help_frame, text=help_text, bg=Theme.BG3, fg=Theme.TEXT3,
                font=("Consolas", 9), justify=tk.LEFT, padx=10, pady=8).pack(anchor="w")
        
        # Text editor
        editor_frame = tk.Frame(drop_frame, bg=Theme.BG3, highlightbackground=Theme.ACCENT,
                               highlightthickness=1)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        self.input_text = scrolledtext.ScrolledText(
            editor_frame, bg=Theme.BG, fg=Theme.TEXT, font=("JetBrains Mono", 11),
            insertbackground=Theme.ACCENT, relief=tk.FLAT, padx=12, pady=12,
            selectbackground=Theme.ACCENT2, selectforeground="#fff"
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Algorithm selection
        algo_frame = tk.Frame(left, bg=Theme.BG2)
        algo_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        tk.Label(algo_frame, text="ALGORITHM", bg=Theme.BG2, fg=Theme.TEXT2,
                font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 8))
        
        algo_btns = tk.Frame(algo_frame, bg=Theme.BG2)
        algo_btns.pack(fill=tk.X)
        
        algorithms = [("1", "RM"), ("2", "DM"), ("3", "EDF"), ("4", "LST")]
        for val, text in algorithms:
            rb = tk.Radiobutton(
                algo_btns, text=text, variable=self.algorithm, value=val,
                bg=Theme.BG2, fg=Theme.TEXT, selectcolor=Theme.BG,
                activebackground=Theme.BG2, activeforeground=Theme.ACCENT,
                font=("Segoe UI", 10, "bold"), indicatoron=False,
                padx=20, pady=6, relief=tk.FLAT, borderwidth=0,
                highlightthickness=0
            )
            rb.pack(side=tk.LEFT, padx=(0, 5))
            
    def _create_right_panel(self, parent):
        right = tk.Frame(parent, bg=Theme.BG2)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = tk.Frame(right, bg=Theme.BG2)
        title_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(title_frame, text="OUTPUT", bg=Theme.BG2, fg=Theme.ACCENT,
                font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
        
        # Tab buttons
        self.tab_var = tk.StringVar(value="chart")
        tab_frame = tk.Frame(title_frame, bg=Theme.BG2)
        tab_frame.pack(side=tk.RIGHT)
        
        for val, text in [("chart", "Chart"), ("log", "Log"), ("budget", "Budget")]:
            btn = tk.Radiobutton(
                tab_frame, text=text, variable=self.tab_var, value=val,
                bg=Theme.BG2, fg=Theme.TEXT2, selectcolor=Theme.BG2,
                activebackground=Theme.BG2, font=("Segoe UI", 9),
                indicatoron=False, padx=12, pady=4,
                command=self._switch_tab
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # Output container
        self.output_frame = tk.Frame(right, bg=Theme.BG)
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self._show_placeholder()
        
    def _switch_tab(self):
        tab = self.tab_var.get()
        if tab == "chart":
            self._show_chart()
        elif tab == "log":
            self._show_log()
        elif tab == "budget":
            self._show_budget()
            
    def _show_placeholder(self):
        for w in self.output_frame.winfo_children():
            w.destroy()
            
        placeholder = tk.Frame(self.output_frame, bg=Theme.BG)
        placeholder.pack(expand=True)
        
        tk.Label(placeholder, text="📊", bg=Theme.BG, fg=Theme.TEXT3,
                font=("Segoe UI", 48)).pack(pady=(50, 10))
        tk.Label(placeholder, text="Click RUN to execute scheduler",
                bg=Theme.BG, fg=Theme.TEXT3, font=("Segoe UI", 11)).pack()
        tk.Label(placeholder, text="Then switch tabs to view results",
                bg=Theme.BG, fg=Theme.TEXT3, font=("Segoe UI", 9)).pack(pady=(5, 50))
                
    def _load_input_file(self):
        self._load_file(INPUT_FILE)
        
    def _load_file(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(1.0, content)
            self.current_file = filepath
            self.file_label.config(text=os.path.basename(filepath))
        else:
            default = """# Real-Time Scheduling Example
# P e p  |  D e p d  |  A r e

P 1 3
P 2 5
A 2 1 (Poller)
"""
            self.input_text.insert(1.0, default)
            
    def _open_file(self):
        filepath = filedialog.askopenfilename(
            title="Open Input File",
            initialdir=DATA_DIR,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            self._load_file(filepath)
            self._set_status(f"Loaded: {os.path.basename(filepath)}", Theme.GREEN)
            
    def _save_input(self):
        content = self.input_text.get(1.0, tk.END)
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(INPUT_FILE, 'w') as f:
            f.write(content)
        self.current_file = INPUT_FILE
        self.file_label.config(text="input.txt")
        self._set_status("Saved to input.txt", Theme.GREEN)
        
    def _run_scheduler(self):
        self._save_input()
        
        if not os.path.exists(EXE_PATH):
            messagebox.showerror("Error", f"Executable not found:\n{EXE_PATH}\n\nRun build.bat first.")
            return
            
        self._set_status("Running scheduler...", Theme.ORANGE)
        self.root.update()
        
        try:
            algo = self.algorithm.get()
            result = subprocess.run(
                [EXE_PATH], input=algo + "\n", cwd=BUILD_DIR,
                capture_output=True, text=True, timeout=30
            )
            
            self.last_output = result.stdout + result.stderr
            
            if "DEADLINE_MISS" in self.last_output:
                self._set_status("Completed with DEADLINE MISS!", Theme.RED)
            else:
                self._set_status("Completed successfully!", Theme.GREEN)
                
            # Auto show chart
            self.tab_var.set("chart")
            self._show_chart()
            
        except subprocess.TimeoutExpired:
            self._set_status("Error: Timeout!", Theme.RED)
        except Exception as e:
            self._set_status(f"Error: {e}", Theme.RED)
            
    def _show_log(self):
        for w in self.output_frame.winfo_children():
            w.destroy()
            
        if not hasattr(self, 'last_output'):
            self._show_placeholder()
            return
            
        log_text = scrolledtext.ScrolledText(
            self.output_frame, bg=Theme.BG, fg=Theme.TEXT,
            font=("JetBrains Mono", 10), relief=tk.FLAT, padx=10, pady=10
        )
        log_text.pack(fill=tk.BOTH, expand=True)
        log_text.insert(1.0, self.last_output)
        log_text.config(state=tk.DISABLED)
        
    def _show_budget(self):
        """Show server budget consumption over time"""
        for w in self.output_frame.winfo_children():
            w.destroy()
            
        if not os.path.exists(OUTPUT_FILE):
            self._show_placeholder()
            return
            
        if not HAS_MATPLOTLIB:
            tk.Label(self.output_frame, text="Matplotlib required for budget view",
                    bg=Theme.BG, fg=Theme.TEXT3, font=("Segoe UI", 11)).pack(expand=True)
            return
            
        try:
            budget_data = self._parse_budget()
            if not budget_data:
                tk.Label(self.output_frame, text="No server budget data found",
                        bg=Theme.BG, fg=Theme.TEXT3, font=("Segoe UI", 11)).pack(expand=True)
                return
                
            self._draw_budget_chart(budget_data)
            
        except Exception as e:
            tk.Label(self.output_frame, text=f"Error: {e}",
                    bg=Theme.BG, fg=Theme.RED, font=("Segoe UI", 10)).pack(expand=True)
            
    def _parse_budget(self):
        """Parse output to extract server budget consumption"""
        budget_events = []
        server_capacity = 2.0  # Default server capacity
        current_budget = server_capacity
        last_replenish = 0
        server_period = 5.0  # Default server period
        
        with open(OUTPUT_FILE, 'r') as f:
            lines = f.readlines()[2:]
            
        times = [0]
        budgets = [server_capacity]
        
        for line in lines:
            parts = line.strip().split('\t')
            if len(parts) < 5:
                continue
                
            try:
                time = float(parts[0])
                task_id = parts[2]
                desc = parts[3]
                event = parts[4]
            except:
                continue
                
            # Check for server replenishment (at period boundaries)
            if time >= last_replenish + server_period:
                last_replenish = (time // server_period) * server_period
                current_budget = server_capacity
                times.append(last_replenish)
                budgets.append(current_budget)
                
            # Server execution consumes budget
            if "Server" in desc and event in ["Running", "ServerExec", "ServerExec(DS)"]:
                current_budget = max(0, current_budget - 0.1)
                times.append(time)
                budgets.append(current_budget)
                
        return {"times": times, "budgets": budgets, "capacity": server_capacity}
        
    def _draw_budget_chart(self, data):
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor(Theme.BG)
        ax.set_facecolor(Theme.BG)
        
        times = data["times"]
        budgets = data["budgets"]
        capacity = data["capacity"]
        
        # Plot budget line
        ax.step(times, budgets, where='post', color=Theme.ACCENT, linewidth=2, label='Budget')
        ax.fill_between(times, budgets, step='post', alpha=0.3, color=Theme.ACCENT)
        
        # Capacity line
        ax.axhline(y=capacity, color=Theme.ORANGE, linestyle='--', linewidth=1, label=f'Capacity ({capacity})')
        ax.axhline(y=0, color=Theme.RED, linestyle='--', linewidth=1, alpha=0.5)
        
        ax.set_xlabel('Time', color=Theme.TEXT, fontsize=10)
        ax.set_ylabel('Server Budget', color=Theme.TEXT, fontsize=10)
        ax.set_title('Server Budget Consumption', color=Theme.ACCENT, fontsize=12, fontweight='bold')
        ax.tick_params(colors=Theme.TEXT2)
        ax.grid(True, linestyle='--', alpha=0.2, color=Theme.TEXT3)
        
        for spine in ax.spines.values():
            spine.set_color(Theme.BG3)
            
        legend = ax.legend(loc='upper right', facecolor=Theme.BG2, edgecolor=Theme.BG3)
        for text in legend.get_texts():
            text.set_color(Theme.TEXT)
            
        ax.set_ylim(-0.2, capacity + 0.5)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.output_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def _show_chart(self):
        for w in self.output_frame.winfo_children():
            w.destroy()
            
        if not os.path.exists(OUTPUT_FILE):
            self._show_placeholder()
            return
            
        if not HAS_MATPLOTLIB:
            tk.Label(self.output_frame, text="Matplotlib required\npip install matplotlib",
                    bg=Theme.BG, fg=Theme.TEXT3, font=("Segoe UI", 11)).pack(expand=True)
            return
            
        try:
            tasks, misses = self._parse_output()
            if not tasks:
                tk.Label(self.output_frame, text="No data in output file",
                        bg=Theme.BG, fg=Theme.TEXT3, font=("Segoe UI", 11)).pack(expand=True)
                return
            self._draw_chart(tasks, misses)
        except Exception as e:
            tk.Label(self.output_frame, text=f"Error: {e}",
                    bg=Theme.BG, fg=Theme.RED, font=("Segoe UI", 10)).pack(expand=True)
            
    def _parse_output(self):
        tasks = {}
        misses = []
        
        with open(OUTPUT_FILE, 'r') as f:
            lines = f.readlines()[2:]
            
        for line in lines:
            parts = line.strip().split('\t')
            if len(parts) < 5:
                continue
                
            try:
                time = float(parts[0])
                task_id = parts[2]
                desc = parts[3]
                event = parts[4]
            except:
                continue
                
            if event in ["Running", "ServerExec", "BackgroundRun", "ServerExec(DS)"]:
                if task_id not in tasks:
                    tasks[task_id] = {"intervals": [], "desc": desc}
                if "Server" in desc:
                    tasks[task_id]["desc"] = desc
                intervals = tasks[task_id]["intervals"]
                if intervals:
                    start, dur = intervals[-1]
                    if abs((start + dur) - time) < 0.001:
                        intervals[-1] = (start, dur + 0.1)
                    else:
                        intervals.append((time, 0.1))
                else:
                    intervals.append((time, 0.1))
            elif event == "DEADLINE_MISS":
                misses.append((time, task_id))
                if task_id not in tasks:
                    tasks[task_id] = {"intervals": [], "desc": "FAILED"}
                    
        return tasks, misses
        
    def _draw_chart(self, tasks, misses):
        colors = {
            "Periodic": Theme.BLUE,
            "Server(Poller)": Theme.ORANGE,
            "Server(Deferrable)": Theme.ORANGE,
            "Aperiodic": Theme.GREEN,
            "Background": Theme.PURPLE,
            "Unknown": Theme.TEXT3,
            "FAILED": Theme.RED
        }
        
        fig, ax = plt.subplots(figsize=(9, 5))
        fig.patch.set_facecolor(Theme.BG)
        ax.set_facecolor(Theme.BG)
        
        sorted_ids = sorted(tasks.keys(), key=lambda x: int(x) if x.lstrip('-').isdigit() else 9999)
        y_labels = []
        y_ticks = []
        task_y = {}
        
        idx = 0
        for tid in sorted_ids:
            if tid == "-1":
                continue
            data = tasks[tid]
            desc = data["desc"]
            intervals = data["intervals"]
            
            color = colors.get(desc, Theme.TEXT3)
            if "Server" in desc:
                color = Theme.ORANGE
                
            ax.broken_barh(intervals, (idx*10, 8), facecolors=color, 
                          edgecolor='white', linewidth=0.5, alpha=0.9)
            y_labels.append(f"{desc} (T{tid})")
            y_ticks.append(idx*10 + 4)
            task_y[tid] = idx*10 + 4
            idx += 1
            
        # Deadline misses
        for time, tid in misses:
            if tid in task_y:
                ax.axvline(x=time, color=Theme.RED, linestyle='--', linewidth=2, alpha=0.8)
                ax.scatter([time], [task_y[tid]], color=Theme.RED, marker='X', s=200, zorder=10)
                
        if idx > 0:
            ax.set_ylim(-5, idx*10 + 5)
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels, color=Theme.TEXT, fontsize=9)
        ax.set_xlabel('Time', color=Theme.TEXT, fontsize=10)
        ax.tick_params(colors=Theme.TEXT2)
        ax.grid(True, axis='x', linestyle='--', alpha=0.2, color=Theme.TEXT3)
        
        for spine in ax.spines.values():
            spine.set_color(Theme.BG3)
            
        ax.set_title('Gantt Chart - Task Execution Timeline', color=Theme.ACCENT, 
                    fontsize=12, fontweight='bold')
        
        # Legend
        patches = []
        seen = set()
        for tid in sorted_ids:
            if tid == "-1":
                continue
            desc = tasks[tid]["desc"]
            if desc not in seen:
                seen.add(desc)
                c = colors.get(desc, Theme.TEXT3)
                if "Server" in desc:
                    c = Theme.ORANGE
                patches.append(mpatches.Patch(color=c, label=desc))
        if misses:
            patches.append(mpatches.Patch(color=Theme.RED, label='DEADLINE MISS'))
            
        if patches:
            legend = ax.legend(handles=patches, loc='upper right', facecolor=Theme.BG2, edgecolor=Theme.BG3)
            for text in legend.get_texts():
                text.set_color(Theme.TEXT)
            
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.output_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def _set_status(self, text, color=None):
        self.status.config(text=text, fg=color or Theme.TEXT2)

def main():
    # Try to use TkinterDnD for drag and drop support
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
        
    app = ModernSchedulerUI(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()
