import customtkinter as ctk
import json
import os
from datetime import datetime
from statistics import mean

DATA_FILE = "weather_data.json"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

FONT = "Fixedsys"
BACKGROUND_COLOR = "#1b1b1b"
TEXT_COLOR = "#00FF00"
BUTTON_COLOR = "#333333"

class WeatherLogApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Weather Log/Bad Code Edition")
        self.geometry("1200x700")

        self.weather_data = []
        self.selected_index = None

        self.load_data()
        self.build_ui()
        self.refresh_log()
        self.update_stats()

    # ---------------- DATA ---------------- #

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            self.weather_data = []
            return

        try:
            with open(DATA_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    self.weather_data = []
                else:
                    self.weather_data = json.loads(content)
        except (json.JSONDecodeError, IOError):
            self.weather_data = []

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.weather_data, f, indent=4)

    # ---------------- UI ---------------- #

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, height=60, bg_color=BACKGROUND_COLOR)
        header.pack(fill="x", padx=10, pady=10)

        self.title_label = ctk.CTkLabel(
            header,
            text="🌦 Weather Log",
            font=ctk.CTkFont(family=FONT, size=26, weight="bold"),
            text_color=TEXT_COLOR
        )
        self.title_label.pack(side="left", padx=20)

        self.time_label = ctk.CTkLabel(header, text="", text_color=TEXT_COLOR)
        self.time_label.pack(side="right", padx=20)
        self.update_time()

        # Main layout
        main = ctk.CTkFrame(self, bg_color=BACKGROUND_COLOR)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        self.left_panel(main)
        self.center_panel(main)
        self.right_panel(main)
        self.bottom_panel()

    # ---------------- LEFT PANEL ---------------- #

    def left_panel(self, parent):
        frame = ctk.CTkFrame(parent, width=300, bg_color=BACKGROUND_COLOR)
        frame.pack(side="left", fill="y", padx=10)

        ctk.CTkLabel(frame, text="Add / Edit Entry", font=(FONT, 18), text_color=TEXT_COLOR).pack(pady=10)

        self.date_entry = ctk.CTkEntry(frame, font=(FONT, 14), fg_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)
        self.date_entry.pack(pady=5, fill="x", padx=10)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        self.temp_entry = ctk.CTkEntry(frame, font=(FONT, 14), placeholder_text="Temperature (°C)", fg_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)
        self.temp_entry.pack(pady=5, fill="x", padx=10)

        self.condition_menu = ctk.CTkOptionMenu(
            frame,
            values=["Sunny", "Cloudy", "Rainy", "Stormy", "Windy"],
            font=(FONT, 14),
            fg_color=BACKGROUND_COLOR,
            text_color=TEXT_COLOR
        )
        self.condition_menu.pack(pady=5)

        self.humidity_slider = ctk.CTkSlider(frame, from_=0, to=100, fg_color="#00FF00")
        self.humidity_slider.pack(pady=10, fill="x", padx=10)

        self.wind_entry = ctk.CTkEntry(frame, font=(FONT, 14), placeholder_text="Wind Speed", fg_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)
        self.wind_entry.pack(pady=5, fill="x", padx=10)

        self.notes_entry = ctk.CTkTextbox(frame, height=80, font=(FONT, 14), fg_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)
        self.notes_entry.pack(pady=10, fill="x", padx=10)

        ctk.CTkButton(frame, text="Add Entry", command=self.add_entry, font=(FONT, 14), fg_color=BUTTON_COLOR, text_color=TEXT_COLOR).pack(pady=5)
        ctk.CTkButton(frame, text="Edit Selected", command=self.edit_entry, font=(FONT, 14), fg_color=BUTTON_COLOR, text_color=TEXT_COLOR).pack(pady=5)
        ctk.CTkButton(frame, text="Delete Selected", command=self.delete_entry, font=(FONT, 14), fg_color=BUTTON_COLOR, text_color=TEXT_COLOR).pack(pady=5)

    # ---------------- CENTER PANEL ---------------- #

    def center_panel(self, parent):
        self.summary = ctk.CTkFrame(parent, bg_color=BACKGROUND_COLOR)
        self.summary.pack(side="left", fill="both", expand=True, padx=10)

        ctk.CTkLabel(
            self.summary,
            text="Daily Summary",
            font=(FONT, 20, "bold"),
            text_color=TEXT_COLOR
        ).pack(pady=10)

        self.summary_label = ctk.CTkLabel(self.summary, text="Select an entry", text_color=TEXT_COLOR)
        self.summary_label.pack(pady=20)

    # ---------------- RIGHT PANEL ---------------- #

    def right_panel(self, parent):
        frame = ctk.CTkFrame(parent, width=300, bg_color=BACKGROUND_COLOR)
        frame.pack(side="right", fill="y", padx=10)

        ctk.CTkLabel(frame, text="Weather History", font=(FONT, 18), text_color=TEXT_COLOR).pack(pady=10)

        self.log_list = ctk.CTkScrollableFrame(frame, fg_color=BACKGROUND_COLOR)
        self.log_list.pack(fill="both", expand=True)

    # ---------------- BOTTOM STATS ---------------- #

    def bottom_panel(self):
        self.stats = ctk.CTkFrame(self, height=100, bg_color=BACKGROUND_COLOR)
        self.stats.pack(fill="x", padx=10, pady=10)

        self.stats_label = ctk.CTkLabel(self.stats, text="", text_color=TEXT_COLOR)
        self.stats_label.pack(pady=10)

    # ---------------- LOGIC ---------------- #

    def add_entry(self):
        try:
            entry = {
                "date": self.date_entry.get(),
                "temperature": float(self.temp_entry.get()),
                "condition": self.condition_menu.get(),
                "humidity": int(self.humidity_slider.get()),
                "wind": self.wind_entry.get(),
                "notes": self.notes_entry.get("1.0", "end").strip()
            }
        except ValueError:
            return

        self.weather_data.append(entry)
        self.save_data()
        self.refresh_log()
        self.update_stats()

    def edit_entry(self):
        if self.selected_index is None:
            return

        self.weather_data[self.selected_index]["temperature"] = float(self.temp_entry.get())
        self.weather_data[self.selected_index]["condition"] = self.condition_menu.get()
        self.weather_data[self.selected_index]["humidity"] = int(self.humidity_slider.get())
        self.weather_data[self.selected_index]["wind"] = self.wind_entry.get()
        self.weather_data[self.selected_index]["notes"] = self.notes_entry.get("1.0", "end")

        self.save_data()
        self.refresh_log()
        self.update_stats()

    def delete_entry(self):
        if self.selected_index is not None:
            self.weather_data.pop(self.selected_index)
            self.selected_index = None
            self.save_data()
            self.refresh_log()
            self.update_stats()
            self.summary_label.configure(text="Entry deleted")

    def refresh_log(self):
        for widget in self.log_list.winfo_children():
            widget.destroy()

        for index, entry in enumerate(self.weather_data):
            btn = ctk.CTkButton(
                self.log_list,
                text=f"{entry['date']} | {entry['temperature']}°C | {entry['condition']}",
                font=(FONT, 14),
                fg_color=BACKGROUND_COLOR,
                text_color=TEXT_COLOR,
                command=lambda i=index: self.load_entry(i)
            )
            btn.pack(fill="x", pady=2)

    def load_entry(self, index):
        self.selected_index = index
        entry = self.weather_data[index]

        self.summary_label.configure(
        text=f"""
        Date: {entry['date']}
        Temp: {entry['temperature']}°C
        Condition: {entry['condition']}
        Humidity: {entry['humidity']}%
        Wind: {entry['wind']}
        Notes: {entry['notes']}
        """
        )

        self.temp_entry.delete(0, "end")
        self.temp_entry.insert(0, entry["temperature"])

    def update_stats(self):
        if not self.weather_data:
            self.stats_label.configure(text="No data yet")
            return

        temps = [e["temperature"] for e in self.weather_data]
        avg_temp = round(mean(temps), 1)

        hottest = max(self.weather_data, key=lambda x: x["temperature"])
        coldest = min(self.weather_data, key=lambda x: x["temperature"])

        self.stats_label.configure(
            text=f"""
        Avg Temp: {avg_temp}°C | 
        Hottest: {hottest['date']} ({hottest['temperature']}°C) |
        Coldest: {coldest['date']} ({coldest['temperature']}°C)
        """
        )

    def update_time(self):
        self.time_label.configure(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.after(1000, self.update_time)


if __name__ == "__main__":
    app = WeatherLogApp()
    app.mainloop()
