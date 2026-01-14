import customtkinter as ctk
import random

FONT = ("Fixedsys", 14)

class CityState:
    def __init__(self):
        self.day = 0
        self.running = False
        self.speed = 1

        self.population = 100
        self.food = 500
        self.energy = 300
        self.money = 200
        self.happiness = 70  # %

        self.base_food_prod = 15
        self.base_energy_prod = 10
        self.base_money_prod = 8

        self.tax_rate = 0.15

        self.events = []
        self.log = []
        self.collapsed = False

    def add_log(self, text):
        self.log.append(f"Day {self.day}: {text}")
        self.log = self.log[-120:]

class SimulationEngine:
    def __init__(self, city: CityState):
        self.city = city

    def tick(self):
        if not self.city.running or self.city.collapsed:
            return

        self.city.day += 1
        self.apply_events()
        self.update_resources()
        self.update_population()
        self.check_status()
        self.random_events()

    def production_modifiers(self):
        food = self.city.base_food_prod
        energy = self.city.base_energy_prod
        money = self.city.base_money_prod

        for e in self.city.events:
            if e["name"] == "Drought":
                food *= 0.4
            elif e["name"] == "Power Outage":
                energy *= 0.5
            elif e["name"] == "Economic Boom":
                money *= 2
            elif e["name"] == "Disease":
                pass

        return food, energy, money

    def update_resources(self):
        pop = self.city.population
        food_p, energy_p, money_p = self.production_modifiers()

        food_change = food_p - pop * 0.5
        energy_change = energy_p - pop * 0.3
        money_change = (money_p * (1 + self.city.tax_rate)) - pop * 0.2

        self.city.food = max(0, int(self.city.food + food_change))
        self.city.energy = max(0, int(self.city.energy + energy_change))
        self.city.money = max(0, int(self.city.money + money_change))

    def update_population(self):
        growth = 0.01 * (self.city.happiness / 100)
        death = 0.005

        if self.city.food < self.city.population:
            death += 0.02
            self.city.happiness -= 2

        if self.city.energy < self.city.population * 0.5:
            growth *= 0.3
            self.city.happiness -= 1

        net = int(self.city.population * (growth - death))
        self.city.population = max(0, self.city.population + net)

        self.city.happiness = max(0, min(100, self.city.happiness))

        if net != 0:
            self.city.add_log(f"Population change: {net:+}")

    def random_events(self):
        if random.random() < 0.04:
            event = random.choice([
                ("Drought", 6),
                ("Power Outage", 4),
                ("Economic Boom", 5),
                ("Disease", 6)
            ])
            self.city.events.append({"name": event[0], "days": event[1]})
            self.city.add_log(f"Event started: {event[0]}")

    def apply_events(self):
        for e in self.city.events[:]:
            if e["name"] == "Disease":
                self.city.population = max(0, self.city.population - 2)

            e["days"] -= 1
            if e["days"] <= 0:
                self.city.events.remove(e)
                self.city.add_log(f"Event ended: {e['name']}")

    def check_status(self):
        if self.city.population <= 0:
            self.city.collapsed = True
            self.city.running = False
            self.city.add_log("CITY COLLAPSED")

        if self.city.money == 0:
            self.city.happiness -= 5
            self.city.add_log("WARNING: Bankruptcy")

class CitySimUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CITYSIM // GREENLINE")
        self.geometry("1050x650")

        self.city = CityState()
        self.engine = SimulationEngine(self.city)

        self.configure(fg_color="#061a06")
        self.create_layout()
        self.after(1000, self.loop)

    def label(self, parent, text):
        return ctk.CTkLabel(parent, text=text, font=FONT, text_color="#00ff66")

    def create_layout(self):
        top = ctk.CTkFrame(self, fg_color="#031003")
        top.pack(fill="x", padx=10, pady=5)

        self.day_label = self.label(top, "Day: 0")
        self.day_label.pack(side="left", padx=10)

        self.status_label = self.label(top, "PAUSED")
        self.status_label.pack(side="right", padx=10)

        main = ctk.CTkFrame(self, fg_color="#061a06")
        main.pack(fill="both", expand=True)

        left = ctk.CTkFrame(main, fg_color="#031003")
        left.pack(side="left", fill="y", padx=5)

        center = ctk.CTkFrame(main, fg_color="#061a06")
        center.pack(side="left", fill="both", expand=True)

        right = ctk.CTkFrame(main, fg_color="#031003")
        right.pack(side="right", fill="y", padx=5)

        self.pop_label = self.label(left, "Population: 0")
        self.pop_label.pack(pady=5)

        self.happy_label = self.label(left, "Happiness: 70%")
        self.happy_label.pack()

        self.food_label = self.label(left, "Food: 0")
        self.food_label.pack()

        self.energy_label = self.label(left, "Energy: 0")
        self.energy_label.pack()

        self.money_label = self.label(left, "Money: 0")
        self.money_label.pack()

        self.food_bar = ctk.CTkProgressBar(center, progress_color="#00aa44")
        self.food_bar.pack(pady=10, fill="x", padx=40)

        self.energy_bar = ctk.CTkProgressBar(center, progress_color="#00ff66")
        self.energy_bar.pack(pady=10, fill="x", padx=40)

        self.money_bar = ctk.CTkProgressBar(center, progress_color="#55ff99")
        self.money_bar.pack(pady=10, fill="x", padx=40)

        ctk.CTkButton(right, text="START / PAUSE", command=self.toggle).pack(pady=5)
        ctk.CTkButton(right, text="Speed x1", command=lambda: self.set_speed(1)).pack()
        ctk.CTkButton(right, text="Speed x2", command=lambda: self.set_speed(2)).pack()
        ctk.CTkButton(right, text="Speed x5", command=lambda: self.set_speed(5)).pack()

        self.log_box = ctk.CTkTextbox(self, height=140, font=FONT)
        self.log_box.pack(fill="x", padx=10, pady=5)

    def toggle(self):
        if not self.city.collapsed:
            self.city.running = not self.city.running

    def set_speed(self, speed):
        self.city.speed = speed

    def loop(self):
        for _ in range(self.city.speed):
            self.engine.tick()
        self.refresh_ui()
        self.after(1000, self.loop)

    def refresh_ui(self):
        self.day_label.configure(text=f"Day: {self.city.day}")
        self.status_label.configure(
            text="RUNNING" if self.city.running else "PAUSED"
        )

        self.pop_label.configure(text=f"Population: {self.city.population}")
        self.happy_label.configure(text=f"Happiness: {self.city.happiness}%")
        self.food_label.configure(text=f"Food: {self.city.food}")
        self.energy_label.configure(text=f"Energy: {self.city.energy}")
        self.money_label.configure(text=f"Money: {self.city.money}")

        self.food_bar.set(min(self.city.food / 500, 1))
        self.energy_bar.set(min(self.city.energy / 300, 1))
        self.money_bar.set(min(self.city.money / 300, 1))

        self.log_box.delete("1.0", "end")
        self.log_box.insert("end", "\n".join(self.city.log))


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = CitySimUI()
    app.mainloop()
