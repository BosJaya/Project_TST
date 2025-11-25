import tkinter as tk
import random
#oke
PARAGRAPHS = [
    "Their politician was, in this moment, a notour paperback. The first armless grouse is, in its own way, a gear.",
    "Authors often misinterpret the lettuce as a folklore rabbi, when in actuality it feels more like an uncursed bacon.",
    "In modern times the first scrawny kitten is, in its own way, an input. An ostrich is the beginner of a roast.",
    "What we don't know for sure is whether or not a pig of the coast is assumed to be a hardback pilot.",
    "An aunt is a bassoon from the right perspective. As far as we can estimate, some posit the melic myanmar to be less than kutcha.",
]
ALL_WORDS = ' '.join(PARAGRAPHS).split()

BG_COLOR, TEXT_MAIN, TEXT_SUB = "#1e1e1e", "#d1d0c5", "#646669"
ERROR_COLOR, ERROR_BG, ACCENT_COLOR = "#ca4754", "#2c0b0e", "#007acc"
FONT_MAIN, FONT_STATS, FONT_SMALL = ("Poppins", 16), ("Poppins", 12, "bold"), ("Poppins", 10)

class SpeedTypingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Speed Typing Game")
        self.root.geometry("700x500")
        self.root.configure(bg=BG_COLOR)

        self.game_mode, self.word_count, self.max_time = "time", 30, 60
        self.time_left, self.timer_running, self.char_index, self.mistakes = 0, False, 0, 0
        self.current_text, self.timer_id, self.active_mode_button = "", None, None

        mode_frame = tk.Frame(self.root, bg=BG_COLOR)
        mode_frame.pack(pady=10)
        
        self.mode_buttons = {}
        modes = [("time", 60), ("words", 30), ("words", 40), ("words", 50)]
        for mode, val in modes:
            text = f"{val} words" if mode == "words" else "time"
            key = val if mode == "words" else "time"
            btn = tk.Button(mode_frame, text=text, font=FONT_SMALL, bg=BG_COLOR, fg=TEXT_SUB, bd=0, relief="flat",
                            activeforeground=TEXT_MAIN, activebackground=BG_COLOR, command=lambda m=mode, v=val: self.set_mode(m, v))
            btn.pack(side="left", padx=10)
            self.mode_buttons[key] = btn
        
        self.text_display = tk.Text(self.root, font=FONT_MAIN, bg=BG_COLOR, fg=TEXT_SUB,
                                    wrap="word", height=8, bd=0, highlightthickness=0)
        self.text_display.pack(pady=30, padx=30)
        self.text_display.tag_config("correct", foreground=TEXT_MAIN)
        self.text_display.tag_config("incorrect", foreground=ERROR_COLOR, background=ERROR_BG)
        self.text_display.tag_config("active", underline=True)

        self.input_entry = tk.Entry(self.root, bd=0, highlightthickness=0, bg=BG_COLOR, fg=BG_COLOR, insertbackground=BG_COLOR)
        self.input_entry.bind("<Key>", self.on_key_press)
        self.input_entry.pack()
        self.root.bind("<Button-1>", lambda _: self.input_entry.focus())

        stats_frame = tk.Frame(self.root, bg=BG_COLOR)
        stats_frame.pack(fill="x", padx=50, pady=20)
        self.stat_labels = {}
        for title in ["Time:", "Mistakes:", "WPM:", "CPM:"]:
            frame = tk.Frame(stats_frame, bg=BG_COLOR)
            frame.pack(side="left", expand=True)
            tk.Label(frame, text=title, font=FONT_SMALL, fg="white", bg=BG_COLOR).pack()
            lbl_val = tk.Label(frame, text="0", font=FONT_STATS, fg="white", bg=BG_COLOR)
            lbl_val.pack()
            self.stat_labels[title] = lbl_val

        tk.Button(self.root, text="Try Again", font=FONT_STATS, bg=BG_COLOR, fg=ACCENT_COLOR, bd=0, relief="flat", command=self.reset_game).pack(pady=10)
        
        self.set_mode("time", 60)
        self.input_entry.focus()

    def load_paragraph(self):
        self.current_text = random.choice(PARAGRAPHS) if self.game_mode == "time" else " ".join(random.sample(ALL_WORDS, min(self.word_count, len(ALL_WORDS))))
        self.text_display.config(state="normal")
        self.text_display.delete("1.0", tk.END)
        self.text_display.insert("1.0", self.current_text)
        self.text_display.config(state="disabled")
        self.text_display.tag_add("active", "1.0", "1.1")

    def on_key_press(self, event):
        is_game_over = (self.game_mode == "time" and self.time_left <= 0) or (self.game_mode == "words" and self.char_index >= len(self.current_text))
        if is_game_over or event.keysym in ("Shift_L", "Shift_R", "Control_L", "Alt_L", "Caps_Lock"):
            return

        if not self.timer_running: self.timer_running = True; self.update_timer()

        if event.keysym == "BackSpace":
            if self.char_index > 0:
                self.text_display.tag_remove("active", f"1.{self.char_index}")
                self.char_index -= 1
                idx = f"1.{self.char_index}"
                if "incorrect" in self.text_display.tag_names(idx): self.mistakes -= 1
                for tag in ("correct", "incorrect"): self.text_display.tag_remove(tag, idx)
                self.text_display.tag_add("active", f"1.{self.char_index + 1}")
        elif len(event.char) == 1 and ord(event.char) >= 32:
            idx = f"1.{self.char_index}"
            self.text_display.tag_remove("active", idx)
            if event.char == self.current_text[self.char_index]:
                self.text_display.tag_add("correct", idx)
            else:
                self.mistakes += 1
                self.text_display.tag_add("incorrect", idx)
            self.char_index += 1
            if self.char_index < len(self.current_text):
                self.text_display.tag_add("active", f"1.{self.char_index + 1}")
            else: # Teks selesai
                self.end_game()
        self.update_stats()

    def update_timer(self):
        self.time_left += -1 if self.game_mode == "time" else 1
        self.update_stats()
        is_time_up = self.game_mode == "time" and self.time_left <= 0
        if is_time_up:
            self.end_game()
        else:
            self.timer_id = self.root.after(1000, self.update_timer)

    def update_stats(self):
        time_elapsed = (self.max_time - self.time_left) if self.game_mode == "time" else self.time_left
        wpm, cpm = 0, 0
        if time_elapsed > 0:
            cpm = round(((self.char_index - self.mistakes) / time_elapsed) * 60)
            wpm = round(cpm / 5)
        self.stat_labels["WPM:"].config(text=str(max(0, wpm)))
        self.stat_labels["CPM:"].config(text=str(max(0, cpm)))
        self.stat_labels["Mistakes:"].config(text=str(self.mistakes))
        self.stat_labels["Time:"].config(text=f"{self.time_left}s")

    def end_game(self):
        self.input_entry.config(state="disabled")
        if self.timer_id: self.root.after_cancel(self.timer_id)
        self.timer_running = False
        self.update_stats()

    def set_mode(self, mode, value):
        self.game_mode = mode
        if mode == "time": self.max_time = value
        else: self.word_count = value
        if self.active_mode_button: self.active_mode_button.config(fg=TEXT_SUB)
        key = mode if mode == 'time' else value
        self.active_mode_button = self.mode_buttons.get(key)
        if self.active_mode_button: self.active_mode_button.config(fg=TEXT_MAIN)
        self.reset_game()

    def reset_game(self):
        if self.timer_id: self.root.after_cancel(self.timer_id)
        self.timer_running = False
        self.char_index, self.mistakes = 0, 0
        self.time_left = self.max_time if self.game_mode == "time" else 0
        self.input_entry.config(state="normal")
        self.input_entry.delete(0, tk.END)
        self.update_stats()
        self.load_paragraph()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedTypingGame(root)
    root.mainloop()
