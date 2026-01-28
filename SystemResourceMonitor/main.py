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

# ---------------- THEME ---------------- #
BG_COLOR = "#020a02"
FRAME_COLOR = "#041404"
NEON_GREEN = "#00ff66"
DIM_GREEN = "#0f3d1e"
WARN_YELLOW = "#d4ff00"
ALERT_RED = "#ff3333"

FONT_MAIN = ("Fixedsys", 12)
FONT_TITLE = ("Fixedsys", 20)
FONT_BIG = ("Fixedsys", 26)

# -------------------------------------- #

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class ResourceMonitor(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("NSR Monitor v1.21")
        self.geometry("1000x650")
        self.configure(fg_color=BG_COLOR)

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
        header = ctk.CTkFrame(self, height=60, fg_color=FRAME_COLOR)
        header.pack(fill="x", padx=10, pady=5)

        self.title_label = ctk.CTkLabel(
            header,
            text="> NIKO'S SYSTEM RESOURCE MONITOR",
            font=FONT_TITLE,
            text_color=NEON_GREEN
        )
        self.title_label.pack(side="left", padx=15)

        self.interval_label = ctk.CTkLabel(
            header,
            text="UPDATE: 1s",
            font=FONT_MAIN,
            text_color=NEON_GREEN
        )
        self.interval_label.pack(side="right", padx=15)

        self.pause_btn = ctk.CTkButton(
            header,
            text="[ PAUSE ]",
            width=90,
            fg_color=BG_COLOR,
            border_color=NEON_GREEN,
            border_width=1,
            text_color=NEON_GREEN,
            command=self.toggle_pause
        )
        self.pause_btn.pack(side="right", padx=10)

    def _build_cards(self):
        self.cards_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.cards_frame.pack(fill="x", padx=10, pady=5)

        self.cpu_card = self._create_card("CPU")
        self.ram_card = self._create_card("RAM")
        self.disk_card = self._create_card("DISK")

        for card in (self.cpu_card, self.ram_card, self.disk_card):
            card.pack(side="left", expand=True, fill="both", padx=5)

    def _create_card(self, title):
        frame = ctk.CTkFrame(self.cards_frame, fg_color=FRAME_COLOR)

        label = ctk.CTkLabel(
            frame,
            text=f"[ {title} ]",
            font=FONT_MAIN,
            text_color=NEON_GREEN
        )
        label.pack(pady=5)

        value = ctk.CTkLabel(
            frame,
            text="0%",
            font=FONT_BIG,
            text_color=NEON_GREEN
        )
        value.pack()

        sub = ctk.CTkLabel(
            frame,
            text="",
            font=FONT_MAIN,
            text_color=DIM_GREEN
        )
        sub.pack()

        bar = ctk.CTkProgressBar(
            frame,
            height=10,
            fg_color=BG_COLOR,
            progress_color=NEON_GREEN
        )
        bar.pack(fill="x", padx=15, pady=10)
        bar.set(0)

        frame.value = value
        frame.sub = sub
        frame.bar = bar

        return frame

    def _build_graph(self):
        self.graph_frame = ctk.CTkFrame(self, fg_color=FRAME_COLOR)
        self.graph_frame.pack(fill="x", padx=10, pady=5)

        self.graph = ctk.CTkCanvas(
            self.graph_frame,
            height=180,
            bg=BG_COLOR,
            highlightthickness=0
        )
        self.graph.pack(fill="both", expand=True)

    def _build_logs(self):
        self.log_frame = ctk.CTkFrame(self, fg_color=FRAME_COLOR)
        self.log_frame.pack(fill="x", padx=10, pady=5)

        self.log_box = ctk.CTkTextbox(
            self.log_frame,
            height=120,
            font=FONT_MAIN,
            fg_color=BG_COLOR,
            text_color=NEON_GREEN
        )
        self.log_box.pack(fill="both", expand=True)
        self.log_box.configure(state="disabled")

    def _build_controls(self):
        controls = ctk.CTkFrame(self, fg_color=BG_COLOR)
        controls.pack(fill="x", padx=10, pady=5)

        clear_btn = ctk.CTkButton(
            controls,
            text="[ CLEAR LOGS ]",
            fg_color=BG_COLOR,
            border_color=NEON_GREEN,
            border_width=1,
            text_color=NEON_GREEN,
            command=self.clear_logs
        )
        clear_btn.pack(side="left", padx=5)

        self.rate_menu = ctk.CTkOptionMenu(
            controls,
            values=list(UPDATE_INTERVALS.keys()),
            fg_color=BG_COLOR,
            button_color=FRAME_COLOR,
            text_color=NEON_GREEN,
            command=self.change_rate
        )
        self.rate_menu.set("1s")
        self.rate_menu.pack(side="right", padx=5)

    # ---------------- LOGIC ---------------- #

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_btn.configure(
            text="[ RESUME ]" if self.paused else "[ PAUSE ]"
        )

    def change_rate(self, choice):
        self.update_rate = UPDATE_INTERVALS[choice]
        self.interval_label.configure(text=f"UPDATE: {choice}")

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
            return ALERT_RED
        elif percent >= 75:
            return WARN_YELLOW
        return NEON_GREEN

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
            self.graph.create_line(
                (i - 1) * step,
                h - (self.cpu_history[i - 1] / 100) * h,
                i * step,
                h - (self.cpu_history[i] / 100) * h,
                fill=NEON_GREEN,
                width=2
            )

        for i in range(1, len(self.ram_history)):
            self.graph.create_line(
                (i - 1) * step,
                h - (self.ram_history[i - 1] / 100) * h,
                i * step,
                h - (self.ram_history[i] / 100) * h,
                fill=DIM_GREEN,
                width=2
            )

    def _check_alerts(self, cpu, ram, disk):
        if cpu > CPU_WARN:
            self.log("!! CPU USAGE CRITICAL")
        if ram > RAM_WARN:
            self.log("!! RAM LIMIT EXCEEDED")
        if disk > DISK_WARN:
            self.log("!! DISK SPACE LOW")

    @staticmethod
    def _gb(value):
        return f"{value / (1024 ** 3):.1f} GB"


if __name__ == "__main__":
    app = ResourceMonitor()
    app.mainloop()
