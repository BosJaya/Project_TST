import tkinter as tk
from typing_backend import TypingGameBackend

BG_COLOR, TEXT_MAIN, TEXT_SUB = "#1e1e1e", "#d1d0c5", "#646669"
ERROR_COLOR, ERROR_BG, ACCENT_COLOR = "#ca4754", "#2c0b0e", "#007acc"
FONT_MAIN, FONT_STATS, FONT_SMALL = ("Poppins", 16), ("Poppins", 12, "bold"), ("Poppins", 10)

class SpeedTypingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Speed Typing Game")
        self.root.geometry("700x500")
        self.root.configure(bg=BG_COLOR)

        self.backend = TypingGameBackend()
        self.timer_id = None
        self.active_mode_button = None

        mode_frame = tk.Frame(self.root, bg=BG_COLOR)
        mode_frame.pack(pady=10)

        self.mode_buttons = {}
        modes = [("time", 60), ("words", 30), ("words", 40), ("words", 50), ("words", 100)]
        for mode, val in modes:
            text = f"{val} words" if mode == "words" else "time"
            key = val if mode == "words" else "time"
            btn = tk.Button(mode_frame, text=text, font=FONT_SMALL, bg=BG_COLOR, fg=TEXT_SUB, bd=0, relief="flat",
                            activeforeground=TEXT_MAIN, activebackground=BG_COLOR,
                            command=lambda m=mode, v=val: self.set_mode(m, v))
            btn.pack(side="left", padx=10)
            self.mode_buttons[key] = btn

        self.text_display = tk.Text(self.root, font=FONT_MAIN, bg=BG_COLOR, fg=TEXT_SUB,
                                    wrap="word", height=8, bd=0, highlightthickness=0)
        self.text_display.pack(pady=30, padx=30)
        self.text_display.tag_config("correct", foreground=TEXT_MAIN)
        self.text_display.tag_config("incorrect", foreground=ERROR_COLOR, background=ERROR_BG)
        self.text_display.tag_config("active", underline=True)

        self.input_entry = tk.Entry(
        self.root,
        bd=0,
        highlightthickness=0,
        bg=BG_COLOR,
        fg=BG_COLOR,
        insertbackground=BG_COLOR,
        disabledbackground=BG_COLOR,
        disabledforeground=BG_COLOR,
        )
        
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

        self.retry_btn = tk.Button(self.root, text="Try Again", font=FONT_STATS, bg=BG_COLOR, fg=ACCENT_COLOR, bd=0, relief="flat", command=self.reset_game)
        self.retry_btn.pack(pady=10)
        self.retry_btn.bind("<Return>", lambda event : self.reset_game())
        
        self.set_mode("time", 60)
        self.input_entry.focus()

    def load_paragraph(self):
        self.current_text = self.backend.current_text
        self.text_display.config(state="normal")
        self.text_display.delete("1.0", tk.END)
        self.text_display.insert("1.0", self.current_text)
        self.text_display.config(state="disabled")
        self.text_display.tag_add("active", "1.0", "1.1")

    def on_key_press(self, event):
        result = self.backend.process_key(event.char, event.keysym)
        if result.get("ignored"):
            return
        if result.get("game_over") and "action" not in result:
            self.end_game()
            return
        if not self.backend.timer_running:
            self.backend.timer_running = True
            self.update_timer()
        if result.get("action") == "backspace":
            idx = result["index"]
            self.text_display.tag_remove("active", f"1.{idx+1}")
            if "incorrect" in self.text_display.tag_names(f"1.{idx}"):
                self.backend.mistakes -= 1
            for tag in ("correct", "incorrect"):
                self.text_display.tag_remove(tag, f"1.{idx}")
            self.text_display.tag_add("active", f"1.{idx + 1}")
        elif result.get("action") == "key_press":
            idx = result["index"]
            self.text_display.tag_remove("active", f"1.{idx}")
            if result["correct"]:
                self.text_display.tag_add("correct", f"1.{idx}")
            else:
                self.text_display.tag_add("incorrect", f"1.{idx}")
                
            if idx + 1 < len(self.current_text):
                self.text_display.tag_add("active", f"1.{idx + 1}")
    
        if result.get("game_over"):
            self.end_game()
    
        
        # if result.get("game_over") or result.get("ignored"):
        #     return

        # if not self.backend.timer_running:
        #     self.backend.timer_running = True
        #     self.update_timer()

        # if result["action"] == "backspace":
        #     idx = result["index"]
        #     self.text_display.tag_remove("active", f"1.{idx+1}")
        #     if "incorrect" in self.text_display.tag_names(f"1.{idx}"):
        #         self.backend.mistakes -= 1
        #     for tag in ("correct", "incorrect"):
        #         self.text_display.tag_remove(tag, f"1.{idx}")
        #     self.text_display.tag_add("active", f"1.{idx + 1}")

        # elif result["action"] == "key_press":
        #     idx = result["index"]
        #     self.text_display.tag_remove("active", f"1.{idx}")
        #     if result["correct"]:
        #         self.text_display.tag_add("correct", f"1.{idx}")
        #     else:
        #         self.backend.mistakes += 1  # This line may be redundant, mistakes handled in backend
        #         self.text_display.tag_add("incorrect", f"1.{idx}")
        #     if idx + 1 < len(self.current_text):
        #         self.text_display.tag_add("active", f"1.{idx + 1}")
        #     else:
        #         self.end_game()

        self.update_stats()

    def update_timer(self):
        self.backend.update_timer()
        self.update_stats()
        if self.backend.is_game_over():
            self.end_game()
        else:
            self.timer_id = self.root.after(1000, self.update_timer)

    def update_stats(self):
        stats = self.backend.get_stats()
        self.stat_labels["WPM:"].config(text=str(stats["WPM"]))
        self.stat_labels["CPM:"].config(text=str(stats["CPM"]))
        self.stat_labels["Mistakes:"].config(text=str(stats["Mistakes"]))
        self.stat_labels["Time:"].config(text=f"{stats['TimeLeft']}s")

    def end_game(self):
        self.input_entry.delete(0, tk.END)
        self.input_entry.config(state="disabled")
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.backend.timer_running = False
        self.update_stats()
        self.input_entry.focus_set()

    def set_mode(self, mode, value):
        if self.active_mode_button:
            self.active_mode_button.config(fg=TEXT_SUB)
        self.active_mode_button = self.mode_buttons.get(value if mode == "words" else "time")
        if self.active_mode_button:
            self.active_mode_button.config(fg=TEXT_MAIN)

        self.backend.set_mode(mode, value)
        self.reset_game()

    def reset_game(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.backend.reset_game()
        self.input_entry.config(state="normal")
        self.input_entry.delete(0, tk.END)
        self.update_stats()
        self.load_paragraph()
        self.input_entry.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedTypingGame(root)
    root.mainloop()
