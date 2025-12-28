import tkinter as tk
from tkinter import ttk, messagebox
import psutil, threading, time, platform, socket
from collections import deque

# ================= Window =================
root = tk.Tk()
root.title("Ultra Gaming System Monitor")
root.geometry("1000x650")
root.resizable(False, False)

# ======= Gaming Theme Colors =======
BG = "#0d1117"
PANEL = "#161b22"
TEXT = "#c9d1d9"
NEON = "#00ffcc"
NEON2 = "#ff0055"

root.configure(bg=BG)

style = ttk.Style()
style.theme_use("default")

# ================= Style =================
style.configure(".", 
    background=PANEL, 
    foreground=TEXT,
    fieldbackground=PANEL,
    borderwidth=0,
    font=("Segoe UI", 10)
)

style.configure("TLabel", background=PANEL, foreground=TEXT)
style.configure("TFrame", background=PANEL)
style.configure("TNotebook", background=BG)
style.configure("TNotebook.Tab", 
    background=PANEL, 
    foreground=TEXT, 
    padding=10
)
style.map("TNotebook.Tab",
    background=[("selected", BG)],
    foreground=[("selected", NEON)]
)

style.configure("TProgressbar", 
    troughcolor="#222", 
    background=NEON
)

style.configure("Treeview", 
    background=PANEL,
    fieldbackground=PANEL,
    foreground=TEXT,
    rowheight=25
)
style.map("Treeview",
    background=[("selected", "#222")],
    foreground=[("selected", NEON)]
)

# ================= Notebook =================
notebook = ttk.Notebook(root)
tabs = {}
for name in ["Overview", "Processes", "Disk", "Network", "System Info", "Settings"]:
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=name)
    tabs[name] = frame
notebook.pack(expand=True, fill="both")

for tab in tabs.values():
    tab.configure(style="TFrame")

# ================= Shared =================
cpu_hist = deque(maxlen=60)

# ================= Overview =================
cpu_lbl = ttk.Label(tabs["Overview"], font=("Segoe UI", 14))
ram_lbl = ttk.Label(tabs["Overview"], font=("Segoe UI", 14))
cpu_bar = ttk.Progressbar(tabs["Overview"], length=700)
ram_bar = ttk.Progressbar(tabs["Overview"], length=700)

cpu_lbl.pack(pady=5)
cpu_bar.pack(pady=5)
ram_lbl.pack(pady=5)
ram_bar.pack(pady=5)

graph = tk.Canvas(tabs["Overview"], bg="#05080f", width=850, height=200)
graph.pack(pady=15)

# ================= Processes =================
cols = ("PID", "Name", "CPU%", "RAM%")
table = ttk.Treeview(tabs["Processes"], columns=cols, show="headings", height=15)
for c in cols:
    table.heading(c, text=c)
    table.column(c, anchor="center", width=200)
table.pack(pady=10)

kill_btn = ttk.Button(tabs["Processes"], text="Kill Selected Process")
kill_btn.pack()

# ================= Disk =================
disk_lbl = ttk.Label(tabs["Disk"], font=("Segoe UI", 12))
disk_bar = ttk.Progressbar(tabs["Disk"], length=700)
disk_lbl.pack(pady=10)
disk_bar.pack(pady=5)

# ================= Network =================
net_lbl = ttk.Label(tabs["Network"], font=("Segoe UI", 12))
net_lbl.pack(pady=15)

# ================= System Info =================
info_box = tk.Text(tabs["System Info"], height=20, width=90, bg=PANEL, fg=TEXT, font=("Segoe UI",10))
info_box.pack(pady=10)

# ================= Settings =================
theme_var = tk.StringVar(value="default")
theme_menu = ttk.Combobox(tabs["Settings"], textvariable=theme_var, values=style.theme_names())
theme_menu.pack(pady=20)

# ================= Functions =================
def draw_graph():
    graph.delete("all")
    pts = list(cpu_hist)
    if len(pts) < 2: return
    w, h = 850, 200
    step = w / (len(pts)-1)
    for i in range(len(pts)-1):
        x1, y1 = i*step, h - pts[i]/100*h
        x2, y2 = (i+1)*step, h - pts[i+1]/100*h
        graph.create_line(x1,y1,x2,y2, fill=NEON, width=2)

def update():
    while True:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        cpu_hist.append(cpu)

        cpu_lbl.config(text=f"CPU Usage: {cpu}%")
        ram_lbl.config(text=f"RAM Usage: {ram}%")
        cpu_bar["value"] = cpu
        ram_bar["value"] = ram

        draw_graph()

        for r in table.get_children(): table.delete(r)
        for p in psutil.process_iter(['pid','name','cpu_percent','memory_percent']):
            try:
                table.insert("", "end", values=(p.info['pid'],p.info['name'],p.info['cpu_percent'],round(p.info['memory_percent'],2)))
            except: pass

        disk = psutil.disk_usage('/')
        disk_lbl.config(text=f"Disk Usage: {disk.percent}%")
        disk_bar["value"] = disk.percent

        net = psutil.net_io_counters()
        net_lbl.config(text=f"Sent: {round(net.bytes_sent/1024/1024,2)} MB | Recv: {round(net.bytes_recv/1024/1024,2)} MB")

        time.sleep(2)

def kill_process():
    sel = table.selection()
    if not sel: return
    pid = int(table.item(sel[0])['values'][0])
    try:
        psutil.Process(pid).terminate()
    except:
        messagebox.showerror("Error","Access Denied")

def change_theme(event):
    style.theme_use(theme_var.get())

theme_menu.bind("<<ComboboxSelected>>", change_theme)

# ================= System Info Fill =================
info = f"""
System: {platform.system()}
Node: {platform.node()}
Release: {platform.release()}
Version: {platform.version()}
Machine: {platform.machine()}
Processor: {platform.processor()}
IP: {socket.gethostbyname(socket.gethostname())}
"""
info_box.insert("1.0", info)

kill_btn.config(command=kill_process)

# ================= Thread =================
threading.Thread(target=update, daemon=True).start()

root.mainloop()
