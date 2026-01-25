import customtkinter as ctk
import psutil
from collections import deque
from datetime import datetime

# ---------------- CONFIG ---------------- #
UPDATE_INTERVALS = {
    "0.5s": 500,
    "1s": 1000,
    "2s": 2000
}

CPU_WARN = 85
RAM_WARN = 85
DISK_WARN = 90

MAX_LOGS = 15
GRAPH_POINTS = 60

# --------------------------------------- #

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class ResourceMonitor(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("System Resource Monitor")
        self.geometry("1000x650")

        self.paused = False
        self.update_rate = UPDATE_INTERVALS["1s"]

        self.cpu_history = deque(maxlen=GRAPH_POINTS)
        self.ram_history = deque(maxlen=GRAPH_POINTS)

        self._build_ui()
        self._update_loop()

    # ---------------- UI BUILD ---------------- #

    def _build_ui(self):
        self._build_header()
        self._build_cards()
        self._build_graph()
        self._build_logs()
        self._build_controls()

    def _build_header(self):
        header = ctk.CTkFrame(self, height=60)
        header.pack(fill="x", padx=10, pady=5)

        self.title_label = ctk.CTkLabel(
            header,
            text="SYSTEM RESOURCE MONITOR",
            font=("Consolas", 20, "bold")
        )
        self.title_label.pack(side="left", padx=15)

        self.interval_label = ctk.CTkLabel(
            header,
            text="Updating every 1s",
            font=("Consolas", 12)
        )
        self.interval_label.pack(side="right", padx=15)

        self.pause_btn = ctk.CTkButton(
            header,
            text="Pause",
            width=80,
            command=self.toggle_pause
        )
        self.pause_btn.pack(side="right", padx=10)

    def _build_cards(self):
        self.cards_frame = ctk.CTkFrame(self)
        self.cards_frame.pack(fill="x", padx=10, pady=5)

        self.cpu_card = self._create_card("CPU")
        self.ram_card = self._create_card("RAM")
        self.disk_card = self._create_card("DISK")

        self.cpu_card.pack(side="left", expand=True, fill="both", padx=5)
        self.ram_card.pack(side="left", expand=True, fill="both", padx=5)
        self.disk_card.pack(side="left", expand=True, fill="both", padx=5)

    def _create_card(self, title):
        frame = ctk.CTkFrame(self.cards_frame, height=140)

        label = ctk.CTkLabel(frame, text=title, font=("Consolas", 16, "bold"))
        label.pack(pady=5)

        value = ctk.CTkLabel(frame, text="0%", font=("Consolas", 26))
        value.pack()

        sub = ctk.CTkLabel(frame, text="", font=("Consolas", 12))
        sub.pack()

        bar = ctk.CTkProgressBar(frame)
        bar.pack(fill="x", padx=15, pady=10)
        bar.set(0)

        frame.value = value
        frame.sub = sub
        frame.bar = bar

        return frame

    def _build_graph(self):
        self.graph_frame = ctk.CTkFrame(self, height=200)
        self.graph_frame.pack(fill="x", padx=10, pady=5)

        self.graph = ctk.CTkCanvas(
            self.graph_frame,
            height=180,
            bg="#0f172a",
            highlightthickness=0
        )
        self.graph.pack(fill="both", expand=True)

    def _build_logs(self):
        self.log_frame = ctk.CTkFrame(self, height=120)
        self.log_frame.pack(fill="x", padx=10, pady=5)

        self.log_box = ctk.CTkTextbox(
            self.log_frame,
            height=120,
            font=("Consolas", 11)
        )
        self.log_box.pack(fill="both", expand=True)
        self.log_box.configure(state="disabled")

    def _build_controls(self):
        controls = ctk.CTkFrame(self)
        controls.pack(fill="x", padx=10, pady=5)

        clear_btn = ctk.CTkButton(
            controls,
            text="Clear Logs",
            command=self.clear_logs
        )
        clear_btn.pack(side="left", padx=5)

        self.rate_menu = ctk.CTkOptionMenu(
            controls,
            values=list(UPDATE_INTERVALS.keys()),
            command=self.change_rate
        )
        self.rate_menu.set("1s")
        self.rate_menu.pack(side="right", padx=5)

    # ---------------- LOGIC ---------------- #

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_btn.configure(text="Resume" if self.paused else "Pause")

    def change_rate(self, choice):
        self.update_rate = UPDATE_INTERVALS[choice]
        self.interval_label.configure(text=f"Updating every {choice}")

    def clear_logs(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{timestamp}] {message}\n")
        self.log_box.configure(state="disabled")
        self.log_box.see("end")

    def colorize(self, percent):
        if percent >= 90:
            return "red"
        elif percent >= 75:
            return "yellow"
        return "green"

    # ---------------- UPDATE LOOP ---------------- #

    def _update_loop(self):
        if not self.paused:
            self.update_stats()
        self.after(self.update_rate, self._update_loop)

    def update_stats(self):
        cpu = psutil.cpu_percent()
        cores = psutil.cpu_count(logical=True)

        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        self.cpu_history.append(cpu)
        self.ram_history.append(mem.percent)

        self._update_card(self.cpu_card, cpu, f"Cores: {cores}")
        self._update_card(
            self.ram_card,
            mem.percent,
            f"{self._gb(mem.used)} / {self._gb(mem.total)}"
        )
        self._update_card(
            self.disk_card,
            disk.percent,
            f"{self._gb(disk.used)} / {self._gb(disk.total)}"
        )

        self._draw_graph()
        self._check_alerts(cpu, mem.percent, disk.percent)

    def _update_card(self, card, percent, subtext):
        card.value.configure(text=f"{percent:.0f}%")
        card.sub.configure(text=subtext)
        card.bar.set(percent / 100)
        card.bar.configure(progress_color=self.colorize(percent))

    def _draw_graph(self):
        self.graph.delete("all")
        w = self.graph.winfo_width()
        h = self.graph.winfo_height()

        step = w / GRAPH_POINTS

        for i in range(1, len(self.cpu_history)):
            x1 = (i - 1) * step
            x2 = i * step
            y1 = h - (self.cpu_history[i - 1] / 100) * h
            y2 = h - (self.cpu_history[i] / 100) * h
            self.graph.create_line(x1, y1, x2, y2, fill="#00ffff", width=2)

        for i in range(1, len(self.ram_history)):
            x1 = (i - 1) * step
            x2 = i * step
            y1 = h - (self.ram_history[i - 1] / 100) * h
            y2 = h - (self.ram_history[i] / 100) * h
            self.graph.create_line(x1, y1, x2, y2, fill="#22c55e", width=2)

    def _check_alerts(self, cpu, ram, disk):
        if cpu > CPU_WARN:
            self.log("WARNING: CPU usage above 85%")
        if ram > RAM_WARN:
            self.log("WARNING: RAM usage critical")
        if disk > DISK_WARN:
            self.log("WARNING: Disk almost full")

    @staticmethod
    def _gb(value):
        return f"{value / (1024 ** 3):.1f} GB"


if __name__ == "__main__":
    app = ResourceMonitor()
    app.mainloop()
