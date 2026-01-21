import re
import time
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG_COLOR = "#06110a"
FG_COLOR = "#00ff88"
ERROR_COLOR = "#ff5555"
HIGHLIGHT_COLOR = "#114422"

FONT = ("Fixedsys", 12)
FONT_SMALL = ("Fixedsys", 10)

class RegexEngine:
    @staticmethod
    def run(pattern: str, text: str, flags: int):
        start = time.time()
        compiled = re.compile(pattern, flags)
        matches = list(compiled.finditer(text))
        duration = (time.time() - start) * 1000
        return matches, duration

class RegexState:
    def __init__(self):
        self.pattern = ""
        self.text = ""
        self.flags = 0
        self.matches = []
        self.error = None
        self.duration_ms = 0

class RegexTester(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.app_state = RegexState()
        self._debounce_id = None

        self.title("Regex Tester // Hacker Mode")
        self.geometry("900x550")
        self.configure(fg_color=BG_COLOR)

        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="REGEX PATTERN", text_color=FG_COLOR, font=FONT).pack(anchor="w", padx=20, pady=(15, 0))

        self.regex_entry = ctk.CTkEntry(self, font=FONT, text_color=FG_COLOR)
        self.regex_entry.pack(fill="x", padx=20)
        self.regex_entry.bind("<KeyRelease>", self.schedule_update)

        flags_frame = ctk.CTkFrame(self, fg_color="transparent")
        flags_frame.pack(anchor="w", padx=20, pady=10)

        self.flag_vars = {
            re.I: ctk.BooleanVar(),
            re.M: ctk.BooleanVar(),
            re.S: ctk.BooleanVar(),
            re.X: ctk.BooleanVar(),
        }

        for flag, label in [
            (re.I, "IGNORECASE"),
            (re.M, "MULTILINE"),
            (re.S, "DOTALL"),
            (re.X, "VERBOSE"),
        ]:
            ctk.CTkCheckBox(
                flags_frame,
                text=label,
                variable=self.flag_vars[flag],
                command=self.schedule_update,
                font=FONT_SMALL,
                text_color=FG_COLOR,
            ).pack(side="left", padx=5)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        left = ctk.CTkFrame(main, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(left, text="TEST TEXT", text_color=FG_COLOR, font=FONT).pack(anchor="w")

        self.text_box = ctk.CTkTextbox(left, font=FONT, text_color=FG_COLOR)
        self.text_box.pack(fill="both", expand=True)
        self.text_box.bind("<KeyRelease>", self.schedule_update)

        right = ctk.CTkFrame(main, width=300, fg_color="transparent")
        right.pack(side="right", fill="y")

        ctk.CTkLabel(right, text="MATCHES", text_color=FG_COLOR, font=FONT).pack(anchor="w")

        self.result_box = ctk.CTkTextbox(right, font=FONT_SMALL, state="disabled")
        self.result_box.pack(fill="both", expand=True)

    def schedule_update(self, *_):
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(200, self.update_regex)

    def update_regex(self):
        self._debounce_id = None

        self.app_state.pattern = self.regex_entry.get()
        self.app_state.text = self.text_box.get("1.0", "end-1c")
        self.app_state.flags = sum(flag for flag, var in self.flag_vars.items() if var.get())

        self.clear_highlights()
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")

        if not self.app_state.pattern:
            self.result_box.configure(state="disabled")
            return

        try:
            matches, duration = RegexEngine.run(
                self.app_state.pattern,
                self.app_state.text,
                self.app_state.flags,
            )

            self.app_state.matches = matches
            self.app_state.duration_ms = duration

            self.result_box.insert(
                "end",
                f"✔ {len(matches)} matches ({duration:.2f} ms)\n\n",
            )

            for i, m in enumerate(matches, 1):
                self.result_box.insert(
                    "end",
                    f"{i}. [{m.start()}–{m.end()}] {m.group(0)}\n",
                )
                self.highlight_match(m)

        except re.error as e:
            self.result_box.insert("end", f"✖ REGEX ERROR:\n{e}")
            self.result_box.configure(text_color=ERROR_COLOR)

        self.result_box.configure(state="disabled")

    def highlight_match(self, match):
        start = f"1.0+{match.start()}c"
        end = f"1.0+{match.end()}c"
        tag = f"match_{match.start()}"

        self.text_box.tag_add(tag, start, end)
        self.text_box.tag_config(tag, background=HIGHLIGHT_COLOR)

    def clear_highlights(self):
        for tag in self.text_box.tag_names():
            self.text_box.tag_delete(tag)

if __name__ == "__main__":
    app = RegexTester()
    app.mainloop()
