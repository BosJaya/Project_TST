import tkinter as tk
from typing_backend import TypingGameBackend 
from PIL import Image, ImageTk, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True 

BG_COLOR, TEXT_MAIN, TEXT_SUB = "#FFFFFF", "#3F3C3C", "#828282" 
BOX_BG_COLOR = "#FFFFFF" 
WALLPAPER_GAP_COLOR = "#227399" 
ERROR_COLOR, ERROR_BG, ACCENT_COLOR = "#ff1028", "#FFFFFF", "#3F51B5" 
ACTIVE_HIGHLIGHT = "#FFD7A9"

FONT_MAIN, FONT_STATS, FONT_SMALL = ("Poppins", 16), ("Poppins", 12, "bold"), ("Poppins", 10)

class SpeedTypingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Belajar Mengetik & Tes Kecepatan Mengetik")
        self.root.configure(bg=WALLPAPER_GAP_COLOR) 

        self.backend = TypingGameBackend()
        self.timer_id = None
        self.current_text = "" 
        
        self.keyboard_image_ref = None 
        self.wallpaper_image_ref = None 
        
        # wp (layer paling blkg)
        self.wallpaper_canvas = tk.Canvas(root, highlightthickness=0, bg=WALLPAPER_GAP_COLOR)
        self.wallpaper_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.root.bind('<Configure>', self.on_resize) 
        
        # Frame Utama 
        main_ui_frame = tk.Frame(self.root, bg=WALLPAPER_GAP_COLOR) 
        main_ui_frame.pack(padx=30, pady=30) 

        # Daftar mode latihan
        self.lesson_modes = {
            "Latihan Baris Tengah": ("home_row_drill", 50), 
            "Latihan Baris Atas": ("top_row_drill", 50),
            "Latihan Baris Bawah": ("bottom_row_drill", 50),
            "Latihan Semua Huruf (A-Z)": ("drill", 50)
        }
        self.lesson_modes_options = list(self.lesson_modes.keys())
        
        # Frame Untuk Pilihan Mode
        mode_frame = tk.Frame(main_ui_frame, bg=BOX_BG_COLOR, padx=10, pady=10, bd=1, relief="solid") 
        mode_frame.pack(fill="x", pady=(0, 20)) 

        # Tombol Tes Kecepatan
        self.test_btn = tk.Button(mode_frame, text="Tes Kecepatan", font=FONT_SMALL, bg=BOX_BG_COLOR, fg=TEXT_MAIN, bd=0, relief="flat",
                        activeforeground=TEXT_MAIN, activebackground=BOX_BG_COLOR,
                        command=lambda m="time", v=60: self.set_mode(m, v))
        self.test_btn.pack(side="left", padx=10)
        
        # 2. Separator
        tk.Label(mode_frame, text=" | ", font=FONT_SMALL, fg=TEXT_SUB, bg=BOX_BG_COLOR).pack(side="left")

        # Elemen Belajar Mengetik
        self.lesson_anchor_label = tk.Label(mode_frame, text="Belajar Mengetik:", font=FONT_SMALL, fg=TEXT_MAIN, bg=BOX_BG_COLOR)
        self.lesson_anchor_label.pack(side="left", padx=(10, 5))
        
        self.selected_lesson = tk.StringVar(root)
        if self.lesson_modes_options:
            self.selected_lesson.set(self.lesson_modes_options[0])

        self.lesson_dropdown = tk.OptionMenu(
            mode_frame, 
            self.selected_lesson, 
            *self.lesson_modes_options,
            command=self.set_lesson_mode_from_dropdown
        )
        self.lesson_dropdown.config(font=FONT_SMALL, bg=BOX_BG_COLOR, fg=TEXT_MAIN, bd=1, relief="flat", activebackground=BOX_BG_COLOR)
        self.lesson_dropdown["menu"].config(font=FONT_SMALL, bg=BOX_BG_COLOR, fg=TEXT_MAIN)
        self.lesson_dropdown.pack(side="left", padx=5)

        self.mode_ui_elements = {
            "time": [self.test_btn],
            "lesson": [self.lesson_anchor_label, self.lesson_dropdown]
        }
        self.active_mode_category = "time" 

        # Frame teks antar muka utama
        text_frame = tk.Frame(main_ui_frame, bg=BOX_BG_COLOR, bd=1, relief="solid")
        text_frame.pack(pady=(0, 20), fill="x") 

        # Teks antar muka utama
        self.text_display = tk.Text(text_frame, font=FONT_MAIN, bg=BOX_BG_COLOR, fg=TEXT_MAIN,
                                    wrap="word", height=6, width=60, bd=0, highlightthickness=0) 
        self.text_display.pack(pady=20, padx=20)
        
        # Tag Betul
        self.text_display.tag_config("correct", foreground=TEXT_MAIN, background=BOX_BG_COLOR) 
        # Tag Salah
        self.text_display.tag_config("incorrect", foreground=ERROR_COLOR, background=ERROR_BG)
        # Tag Indikator
        self.text_display.tag_config("active", foreground=TEXT_MAIN, background=ACTIVE_HIGHLIGHT) 
    
        self.input_entry = tk.Entry(
        text_frame, bd=0, highlightthickness=0, 
        width=1, 
        bg=BOX_BG_COLOR, fg=BOX_BG_COLOR,
        insertbackground=BOX_BG_COLOR, disabledbackground=BOX_BG_COLOR, disabledforeground=BOX_BG_COLOR,
        )
        self.input_entry.bind("<Key>", self.on_key_press)
        self.input_entry.pack() 
        self.root.bind("<Button-1>", lambda _: self.input_entry.focus())

        stats_frame_outer = tk.Frame(main_ui_frame, bg=BOX_BG_COLOR, bd=1, relief="solid")
        stats_frame_outer.pack(fill="x", pady=(0, 20)) 
        
        stats_frame_inner = tk.Frame(stats_frame_outer, bg=BOX_BG_COLOR, padx=10, pady=10)
        stats_frame_inner.pack(fill="x")
        
        self.stat_labels = {}
        for title in ["Waktu:", "Kesalahan:", "KPM:", "HPM:"]: 
            frame = tk.Frame(stats_frame_inner, bg=BOX_BG_COLOR) 
            frame.pack(side="left", expand=True)
            tk.Label(frame, text=title, font=FONT_SMALL, fg=TEXT_MAIN, bg=BOX_BG_COLOR).pack() 
            lbl_val = tk.Label(frame, text="0", font=FONT_STATS, fg=TEXT_MAIN, bg=BOX_BG_COLOR) 
            lbl_val.pack() 
            self.stat_labels[title] = lbl_val
            
        keyboard_frame = tk.Frame(main_ui_frame, bg=BOX_BG_COLOR, bd=1, relief="solid")
        keyboard_frame.pack(fill="x")

        # Keyboard Canvas 
        self.keyboard_canvas = tk.Canvas(keyboard_frame, width=700, height=200, bg=BOX_BG_COLOR, highlightthickness=0) 
        self.keyboard_canvas.pack(pady=15, padx=10) 
        self.load_keyboard_visualizer() 

        # Ganti ke Tab+Enter
        self.root.bind("<Return>", lambda event : self.reset_game())
        
        # Wallpaper
        self.root.update_idletasks() 
        self.load_wallpaper() 
        
        self.set_mode("time", 60)
        self.input_entry.focus()
        
    def load_wallpaper(self):
        self.wallpaper_canvas.delete("all")
        try:
            pil_img = Image.open("wallpaper.png")
            self.original_wallpaper_size = pil_img.size
            self.resize_wallpaper(self.root.winfo_width(), self.root.winfo_height())
            
        except FileNotFoundError:
            self.wallpaper_canvas.config(bg=WALLPAPER_GAP_COLOR)
            print("Peringatan: File wallpaper.png tidak ditemukan.")
        except Exception as e:
            print(f"Peringatan saat memuat wallpaper: {e}")

    def resize_wallpaper(self, width, height):
        if not hasattr(self, 'original_wallpaper_size') or width <= 1 or height <= 1:
            return

        original_width, original_height = self.original_wallpaper_size
        
        ratio_w = width / original_width
        ratio_h = height / original_height
        
        resize_ratio = max(ratio_w, ratio_h)
        
        new_width = int(original_width * resize_ratio)
        new_height = int(original_height * resize_ratio)

        try:
            pil_img = Image.open("wallpaper.png")
            resized_img = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.wallpaper_image_ref = ImageTk.PhotoImage(resized_img)
            
            self.wallpaper_canvas.delete("wallpaper_bg")
            
            center_x = width // 2
            center_y = height // 2
            
            self.wallpaper_canvas.create_image(
                center_x, 
                center_y, 
                image=self.wallpaper_image_ref, 
                tags="wallpaper_bg"
            )
            self.wallpaper_canvas.config(width=width, height=height) 

        except Exception:
            pass

    def on_resize(self, event):
        if event.widget == self.root:
            if self.root.winfo_width() > 1 and self.root.winfo_height() > 1:
                 self.resize_wallpaper(self.root.winfo_width(), self.root.winfo_height())
            
    def set_lesson_mode_from_dropdown(self, lesson_name):
        mode, value = self.lesson_modes[lesson_name]
        self.set_mode(mode, value)
        
    def update_mode_highlight(self, current_mode_category):
        for category, elements in self.mode_ui_elements.items():
            
            if category == current_mode_category:
                target_color = TEXT_SUB 
            else:
                target_color = TEXT_MAIN 

            for element in elements:
                if isinstance(element, (tk.Button, tk.Label, tk.OptionMenu)):
                    element.config(fg=target_color)
        
        self.active_mode_category = current_mode_category

    def load_paragraph(self):
        self.backend.load_paragraph()
        self.current_text = self.backend.current_text
        self.text_display.config(state="normal")
        self.text_display.delete("1.0", tk.END)
        self.text_display.insert("1.0", self.current_text)
        self.text_display.tag_add("active", "1.0", "1.1") 
        
        self.text_display.config(state="disabled")

    def load_keyboard_visualizer(self):
        self.keyboard_canvas.delete("all")
        try:
            pil_img = Image.open("Image.png")
            canvas_width = 700 
            original_width, original_height = pil_img.size
            new_height = int(original_height * (canvas_width / original_width))
            self.keyboard_canvas.config(height=new_height)

            pil_img = pil_img.resize((canvas_width, new_height), Image.Resampling.LANCZOS)
            self.keyboard_image_ref = ImageTk.PhotoImage(pil_img)
            self.keyboard_canvas.create_image(
                canvas_width // 2, new_height // 2, 
                image=self.keyboard_image_ref, 
                tags="keyboard_bg"
            )
            
        except FileNotFoundError:
            self.keyboard_canvas.create_text(350, 100, text="GAMBAR KEYBOARD TIDAK DITEMUKAN (Cek Image.png)", fill="#FF5733", font=("Poppins", 14, "bold"))
            return
        except ImportError:
            self.keyboard_canvas.create_text(350, 100, text="INSTAL LIBRARY: pip install Pillow", fill="#FF5733", font=("Poppins", 14, "bold"))
            return

    def highlight_key(self):
        pass


    def on_key_press(self, event):
        result = self.backend.process_key(event.char, event.keysym)
        
        if result.get("ignored"):
            return
            
        if self.backend.timer_running and self.timer_id is None:
            self.update_timer()

        if result.get("action") == "backspace":
            idx = result["index"]
            self.text_display.tag_remove("active", f"1.{idx+1}")
            self.text_display.tag_add("active", f"1.{idx}")
            
            for tag in ("correct", "incorrect"):
                if tag in self.text_display.tag_names(f"1.{idx}"):
                    self.text_display.tag_remove(tag, f"1.{idx}")

            self.text_display.tag_remove("correct", f"1.{idx}")
            self.text_display.tag_remove("incorrect", f"1.{idx}")
                    
            self.update_stats()
                    
        elif result.get("action") == "key_press":
            idx = result["index"]
            self.text_display.tag_remove("active", f"1.{idx}")   
            tag = "correct" if result["correct"] else "incorrect"
            self.text_display.tag_add(tag, f"1.{idx}")

            if idx + 1 < len(self.current_text):
                self.text_display.tag_add("active", f"1.{idx + 1}")
        
        self.highlight_key()
        self.update_stats()
        
        if result.get("game_over"):
            self.end_game()

    def update_timer(self):
        self.backend.update_timer()
        self.update_stats()
        
        if self.backend.is_game_over():
            self.end_game()
        else:
            self.timer_id = self.root.after(1000, self.update_timer)

    def update_stats(self):
        stats = self.backend.get_stats()
        
        time_display = f"{stats['TimeLeft']}s" 
        
        if self.backend.game_mode != "time":
            total_seconds = stats['TimeLeft']
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            time_display = f"{minutes:02d}:{seconds:02d}"

        self.stat_labels["KPM:"].config(text=str(stats["WPM"]))
        self.stat_labels["HPM:"].config(text=str(stats["CPM"]))
        self.stat_labels["Kesalahan:"].config(text=str(stats["Mistakes"]))
        self.stat_labels["Waktu:"].config(text=time_display)

    def end_game(self):
        self.input_entry.delete(0, tk.END)
        self.input_entry.config(state="disabled")
        
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
            
        self.backend.timer_running = False
        self.update_stats()
        self.text_display.tag_remove("active", "1.0", tk.END)
        self.highlight_key()
        self.retry_btn.focus_set()

    def set_mode(self, mode, value):
        
        if mode == "time":
            category = "time"
        else:
            category = "lesson"
            
        self.update_mode_highlight(category)
        
        self.backend.set_mode(mode, value)
        self.reset_game()

    def reset_game(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        
        self.backend.reset_game()
        self.input_entry.config(state="normal")
        self.input_entry.delete(0, tk.END)
        
        self.update_stats()
        self.load_paragraph()
        self.input_entry.focus_set()
        self.highlight_key()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedTypingGame(root)
    root.geometry("750x650")
    root.mainloop()