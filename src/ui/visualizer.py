import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
import os

# --- PATH CONFIGURATION ---
script_dir = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.abspath(os.path.join(script_dir, "../../data/output.txt"))
CONFIG_FILE = os.path.abspath(os.path.join(script_dir, "../../data/input.txt"))
OUTPUT_IMAGE = os.path.abspath(os.path.join(script_dir, "../../data/schedule_chart.png"))

# Colors
COLORS = {
    "Periodic": "tab:blue",
    "Server(Poller)": "tab:orange",
    "Server(Deferrable)": "tab:orange",
    "Aperiodic": "tab:green",
    "Background": "tab:purple",
    "Unknown": "tab:gray",
    "FAILURE": "red",
    "Server": "tab:orange"
}

def detect_input_policy(filename):
    """Scans input file to detect if Poller or Deferrable was requested."""
    policy = "Background (None)"
    if not os.path.exists(filename): return "Unknown Input"
    try:
        with open(filename, 'r') as f:
            for line in f.readlines():
                content = line.split('#')[0]
                if "(Poller)" in content: policy = "Polling Server"
                elif "(Deferrable)" in content: policy = "Deferrable Server"
    except: pass
    return policy

def parse_data(filename):
    tasks = {} 
    misses = [] 
    
    if not os.path.exists(filename):
        print(f"Error: File {filename} not found.")
        return None, None

    with open(filename, 'r') as f:
        # Skip header lines
        lines = f.readlines()[2:] 
        
        for line in lines:
            parts = line.strip().split('\t')
            if len(parts) < 5: continue
            
            try:
                # FLOAT PARSING FOR 0.1 QUANTUM
                time = float(parts[0])
                task_id = parts[2]
                desc = parts[3]
                event = parts[4]
            except ValueError: continue
            
            # 1. Handle Execution Events
            if event in ["Running", "ServerExec", "BackgroundRun", "ServerExec(DS)"]:
                if task_id not in tasks:
                    tasks[task_id] = {"intervals": [], "desc": desc}
                
                # Upgrade Description if Server detected
                if "Server" in desc and "Server" not in tasks[task_id]["desc"]:
                    tasks[task_id]["desc"] = desc

                current_intervals = tasks[task_id]["intervals"]
                
                # Merge logic for floats (check epsilon 0.0001)
                if current_intervals:
                    start, dur = current_intervals[-1]
                    # If (Start + Duration) is roughly equal to Current Time
                    if abs((start + dur) - time) < 0.0001:
                        current_intervals.pop()
                        current_intervals.append((start, dur + 0.1)) # Extend by 0.1
                    else:
                        current_intervals.append((time, 0.1))
                else:
                    current_intervals.append((time, 0.1))
            
            # 2. Handle Deadline Misses
            elif event == "DEADLINE_MISS":
                misses.append((time, task_id))
                if task_id not in tasks:
                     tasks[task_id] = {"intervals": [], "desc": "Failed Task"}

    return tasks, misses

def plot_gantt(tasks, misses, policy_name):
    if not tasks: return

    fig, ax = plt.subplots(figsize=(12, 6))
    y_labels = []
    y_ticks = []
    
    # Sort: Server (ID 999) at the top
    sorted_ids = sorted(tasks.keys(), key=lambda x: int(x) if x != '999' else 999999)
    
    task_y_map = {} 
    seen_types = set()

    for i, task_id in enumerate(sorted_ids):
        data = tasks[task_id]
        desc = data["desc"]
        intervals = data["intervals"]
        seen_types.add(desc)

        # Color Lookup
        color = COLORS.get(desc, "tab:gray")
        if "Server" in desc: color = COLORS["Server"]
        
        # Draw Bars
        ax.broken_barh(intervals, (i * 10, 9), facecolors=color, edgecolor='black')
        
        y_labels.append(f"{desc}\n(ID: {task_id})")
        y_ticks.append(i * 10 + 4.5)
        task_y_map[task_id] = i * 10 + 4.5

    # Plot Misses
    for time, task_id in misses:
        if task_id in task_y_map:
            y_pos = task_y_map[task_id]
            ax.axvline(x=time, color='red', linestyle='--', linewidth=2, alpha=0.8)
            ax.scatter([time], [y_pos], color='red', marker='x', s=100, zorder=10)

    # Formatting
    ax.set_ylim(0, len(tasks) * 10 + 10)
    
    max_run = max([i[0]+i[1] for t in tasks.values() for i in t["intervals"]]) if tasks else 0
    max_miss = max([m[0] for m in misses]) if misses else 0
    ax.set_xlim(0, max(max_run, max_miss) + 0.5)
    
    ax.set_xlabel('Time (Seconds)')
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.grid(True, axis='x', linestyle='--', alpha=0.7)
    
    # Legend
    patches = []
    for desc_type in sorted(seen_types):
        c = COLORS.get(desc_type, "tab:gray")
        if "Server" in desc_type: c = COLORS["Server"]
        patches.append(mpatches.Patch(color=c, label=desc_type))
    
    if misses: patches.append(mpatches.Patch(color='red', label='DEADLINE MISS'))
        
    plt.legend(handles=patches, loc='upper right')
    plt.title(f'Real-Time Schedule Execution\nMode: {policy_name}')
    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE)

if __name__ == "__main__":
    print("Generating Chart...")
    policy = detect_input_policy(CONFIG_FILE)
    tasks, misses = parse_data(DATA_FILE)
    if tasks:
        plot_gantt(tasks, misses, policy)
        print(f"Done. Saved to {OUTPUT_IMAGE}")
    else:
        print("No data found to plot.")