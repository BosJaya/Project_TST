import random
import time

PARAGRAPHS = [
    "pemanasan global merupakan peningkatan suhu rata rata di permukaan bumi yang terjadi akibat penumpukan gas rumah kaca di atmosfer. perubahan iklim ini membawa dampak serius bagi kelangsungan hidup manusia, hewan, dan tumbuhan. solusi utama untuk mengatasi masalah ini adalah dengan mengurangi emisi karbon secara global.",
    "batik adalah warisan budaya tak benda dari Indonesia yang diakui oleh unesco. setiap motif batik memiliki filosofi dan sejarahnya sendiri, yang seringkali merefleksikan kearifan lokal daerah asalnya. proses pembuatan batik, terutama batik tulis, membutuhkan ketelitian dan waktu yang lama.",
    "kopi Indonesia telah dikenal luas di seluruh dunia karena keunikan rasa dan varietasnya yang beragam. Mulai dari Gayo Aceh hingga Kopi Toraja Sulawesi, setiap daerah menawarkan karakteristik rasa yang khas. aktivitas minum kopi kini bukan hanya sekadar kebiasaan, tetapi telah menjadi bagian dari gaya hidup modern.",
    "literasi digital adalah kemampuan untuk menemukan, mengevaluasi, dan mengomunikasikan informasi menggunakan teknologi digital. keterampilan ini sangat penting di era informasi saat ini. penguasaan literasi digital membantu individu berpartisipasi penuh dalam masyarakat yang semakin terhubung.",
    "revolusi industri ditandai dengan integrasi teknologi siber dan fisik, termasuk kecerdasan buatan iot dan komputasi awan. transformasi ini mengubah cara kita bekerja, berinteraksi, dan hidup, menuntut adaptasi cepat dari semua sektor industri dan pendidikan di seluruh dunia."
]

DRILL_CHARS = "a s d f j k l ; q w e r t y u i o p z x c v b n m , . /"
DRILL_PATTERNS = [c * 3 + ' ' for c in DRILL_CHARS.split()]

HOME_ROW_CHARS = "a s d f j k l ;"
TOP_ROW_CHARS = "q w e r t y u i o p"
BOTTOM_ROW_CHARS = "z x c v b n m , . /"

HOME_ROW_PATTERNS = [c * 3 + ' ' for c in HOME_ROW_CHARS.split()]
TOP_ROW_PATTERNS = [c * 3 + ' ' for c in TOP_ROW_CHARS.split()]
BOTTOM_ROW_PATTERNS = [c * 3 + ' ' for c in BOTTOM_ROW_CHARS.split()]

ALL_WORDS = ' '.join(PARAGRAPHS).replace('.', '').replace(',', '').split()

class TypingGameBackend:
    def __init__(self):
        self.game_mode = "time" 
        self.word_count = 30
        self.max_time = 60

        self.time_left = 0
        self.start_time = 0
        self.timer_running = False
        self.char_index = 0
        self.mistakes = 0
        self.game_over_flag = False 
        
        self.current_text = ""

    def set_mode(self, mode, value):
        self.game_mode = mode
        if mode == "time":
            self.max_time = value
            self.word_count = 0
        else:
            self.word_count = value
            self.max_time = 0
        self.reset_game()

    def reset_game(self):
        self.char_index = 0
        self.mistakes = 0
        self.start_time = 0
        self.time_left = self.max_time if self.game_mode == "time" else 0
        self.timer_running = False
        self.game_over_flag = False 
        self.load_paragraph()

    def generate_drill_text(self, patterns):
        drill_text = "".join(random.choices(patterns, k=self.word_count * 3))
        return drill_text.strip()
        
    def load_paragraph(self):
        if self.game_mode == "time":
            self.current_text = " ".join(random.choices(ALL_WORDS, k=300))
        elif self.game_mode == "drill":
            self.current_text = self.generate_drill_text(DRILL_PATTERNS)
        elif self.game_mode == "home_row_drill":
            self.current_text = self.generate_drill_text(HOME_ROW_PATTERNS)
        elif self.game_mode == "top_row_drill":
            self.current_text = self.generate_drill_text(TOP_ROW_PATTERNS)
        elif self.game_mode == "bottom_row_drill":
            self.current_text = self.generate_drill_text(BOTTOM_ROW_PATTERNS)
        else:
            self.current_text = " ".join(random.sample(ALL_WORDS, min(self.word_count, len(ALL_WORDS))))

    def process_key(self, char, keysym):
        if (self.game_over_flag) and keysym != "Return":
            return {"game_over": True}

        if keysym in ("Caps_Lock",):
            return {"ignored": True}
        
        if keysym == "BackSpace":
            if self.char_index > 0:
                self.char_index -= 1
                idx = self.char_index
                return {"action": "backspace", "index": idx}
            else:
                return {"ignored": True}

        if len(char) == 1 and ord(char) >= 32:
            
            if not self.timer_running:
                self.start_time = time.time()
                self.timer_running = True
                
            idx = self.char_index
            correct_char = self.current_text[self.char_index] if self.char_index < len(self.current_text) else None
            is_correct = (char == correct_char)
            if not is_correct:
                self.mistakes += 1
            
            self.char_index += 1
            game_over = self.char_index >= len(self.current_text)

            if game_over and self.game_mode != "time":
                 self.timer_running = False 
                 self.game_over_flag = True 
            
            return {"action": "key_press", "index": idx, "correct": is_correct, "game_over": game_over}

        return {"ignored": True}

    def update_timer(self):
        if not self.timer_running:
            return
            
        time_elapsed = int(time.time() - self.start_time)
        
        if self.game_mode == "time":
            self.time_left = max(0, self.max_time - time_elapsed)
            if self.time_left <= 0:
                self.timer_running = False
                self.game_over_flag = True 
        else:
            self.time_left = time_elapsed 

    def get_stats(self):
        if self.game_mode == "time":
            time_elapsed = self.max_time if self.game_over_flag else (self.max_time - self.time_left)
        else:
            time_elapsed = self.time_left if self.char_index > 0 else 0
            
        wpm, cpm = 0, 0
        net_chars = self.char_index - self.mistakes 
        
        if time_elapsed > 0:
            cpm = round((net_chars / time_elapsed) * 60)
            wpm = round(cpm / 5)
            
        return {
            "WPM": max(0, wpm), 
            "CPM": max(0, cpm), 
            "Mistakes": self.mistakes, 
            "TimeLeft": self.time_left, 
            "TimeElapsed": time_elapsed, 
        }

    def is_game_over(self):
        return self.game_over_flag or (self.game_mode != "time" and self.char_index >= len(self.current_text) and not self.timer_running)
    
    