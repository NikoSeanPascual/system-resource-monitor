import customtkinter as ctk
import random

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Pig Dice Game (Scuffed Edition)")
app.geometry("420x520")

players = ["Player 1", "Computer"]
scores = [0, 0]
current_player = 0
current_turn_score = 0
game_over = False

WIN_SCORE = ctk.IntVar(value=100)
AI_ENABLED = ctk.BooleanVar(value=True)

# -------------------- GAME LOGIC --------------------

def update_labels():
    player_label.configure(
        text=f"▶ Current Player: {players[current_player]}",
        text_color="yellow"
    )

    score_label.configure(
        text=f"{players[0]}: {scores[0]}  |  {players[1]}: {scores[1]}"
    )

    turn_score_label.configure(text=f"Turn Score: {current_turn_score}")

def set_buttons(state):
    roll_button.configure(state=state)
    hold_button.configure(state=state)

def animate_dice(final_roll, count=6):
    if count == 0:
        dice_label.configure(text=f"🎲 Rolled: {final_roll}")
        process_roll(final_roll)
        return

    dice_label.configure(text=f"🎲 Rolling... {random.randint(1,6)}")
    app.after(80, animate_dice, final_roll, count - 1)

def roll_dice():
    if game_over or WIN_SCORE.get() <= 0:
        return

    final_roll = random.randint(1, 6)
    animate_dice(final_roll)

def process_roll(roll):
    global current_turn_score
    if roll == 1:
        current_turn_score = 0
        end_turn()
    else:
        current_turn_score += roll
        update_labels()

def hold():
    global current_turn_score, game_over

    if game_over or WIN_SCORE.get() <= 0:
        return

    scores[current_player] += current_turn_score
    current_turn_score = 0

    if scores[current_player] >= WIN_SCORE.get():
        dice_label.configure(text=f"🏆 {players[current_player]} Wins!")
        game_over = True
        set_buttons("disabled")
        return

    end_turn()

def end_turn():
    global current_player, current_turn_score
    current_turn_score = 0
    current_player = (current_player + 1) % 2
    update_labels()

    if AI_ENABLED.get() and current_player == 1 and not game_over:
        set_buttons("disabled")
        app.after(800, ai_turn)
    else:
        set_buttons("normal")

def ai_turn():
    global current_turn_score

    if game_over:
        return

    roll = random.randint(1, 6)
    dice_label.configure(text=f"🎲 AI Rolled: {roll}")

    if roll == 1:
        current_turn_score = 0
        end_turn()
    elif current_turn_score < 15 and scores[1] + current_turn_score < WIN_SCORE.get():
        current_turn_score += roll
        update_labels()
        app.after(500, ai_turn)
    else:
        hold()

def validate_win_score(*args):
    try:
        value = WIN_SCORE.get()
        if value <= 0:
            raise ValueError
        if not game_over:
            set_buttons("normal")
    except:
        set_buttons("disabled")

def reset_game():
    global scores, current_player, current_turn_score, game_over

    scores = [0, 0]
    current_player = 0
    current_turn_score = 0
    game_over = False

    dice_label.configure(text="🎲 Roll the dice!")
    set_buttons("normal")
    validate_win_score()
    update_labels()

WIN_SCORE.trace_add("write", validate_win_score)

# -------------------- UI --------------------

title = ctk.CTkLabel(app, text="Pig Dice Game", font=("Arial", 26, "bold"))
title.pack(pady=10)

player_label = ctk.CTkLabel(app, text="", font=("Arial", 16))
player_label.pack(pady=5)

score_label = ctk.CTkLabel(app, text="", font=("Arial", 14))
score_label.pack(pady=5)

turn_score_label = ctk.CTkLabel(app, text="", font=("Arial", 14))
turn_score_label.pack(pady=5)

dice_label = ctk.CTkLabel(app, text="🎲 Roll the dice!", font=("Arial", 22))
dice_label.pack(pady=15)

roll_button = ctk.CTkButton(app, text="Roll Dice", command=roll_dice)
roll_button.pack(pady=8)

hold_button = ctk.CTkButton(app, text="Hold", command=hold)
hold_button.pack(pady=8)

reset_button = ctk.CTkButton(app, text="🔄 New Game", command=reset_game)
reset_button.pack(pady=10)

settings_frame = ctk.CTkFrame(app)
settings_frame.pack(pady=10)

ctk.CTkLabel(settings_frame, text="Win Score:").grid(row=0, column=0, padx=5)
ctk.CTkEntry(settings_frame, textvariable=WIN_SCORE, width=80).grid(row=0, column=1)

ctk.CTkCheckBox(
    settings_frame,
    text="Player vs Computer",
    variable=AI_ENABLED
).grid(row=1, column=0, columnspan=2, pady=5)

# Initial state
update_labels()
validate_win_score()

app.mainloop()
