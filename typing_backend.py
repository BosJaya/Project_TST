import random

PARAGRAPHS = [
    "Their politician was, in this moment, a notour paperback. The first armless grouse is, in its own way, a gear.",
    "Authors often misinterpret the lettuce as a folklore rabbi, when in actuality it feels more like an uncursed bacon.",
    "In modern times the first scrawny kitten is, in its own way, an input. An ostrich is the beginner of a roast.",
    "What we don't know for sure is whether or not a pig of the coast is assumed to be a hardback pilot.",
    "An aunt is a bassoon from the right perspective. As far as we can estimate, some posit the melic myanmar to be less than kutcha.",
    "The important on gate surfaces around us are not just random access memory; they might also be digital poodles.",
    "A good example of this is the curious case of a wisecracking detective.",
    "The first humble cupcake is, in its own way, a motherboard. A pancake is a microchip from the right perspective."
    "Moreover, a savvy detective living in a large city will be able to provide insight into the case.",
    "Begging the question of whether a savvy detective is a microchip or a cupcake has puzzled philosophers for years."
]  
ALL_WORDS = ' '.join(PARAGRAPHS).split()

class TypingGameBackend:
    def __init__(self):
        self.game_mode = "time"
        self.word_count = 30
        self.max_time = 60
        self.time_left = 0
        self.timer_running = False
        self.char_index = 0
        self.mistakes = 0
        self.current_text = ""
        self.timer_id = None

    def set_mode(self, mode, value):
        self.game_mode = mode
        if mode == "time":
            self.max_time = value
        else:
            self.word_count = value
        self.reset_game()

    def reset_game(self):
        self.char_index = 0
        self.mistakes = 0
        self.time_left = self.max_time if self.game_mode == "time" else 0
        self.timer_running = False
        self.load_paragraph()

    def load_paragraph(self):
        if self.game_mode == "time":
            self.current_text = ' '.join(random.sample(ALL_WORDS, min(50, len(ALL_WORDS))))
        else: 
            self.current_text = ' '.join(random.sample(ALL_WORDS, self.word_count))
            
    def process_key(self, char, keysym):
        if (self.game_mode == "time" and self.time_left <= 0) or (self.game_mode == "words" and self.char_index >= len(self.current_text)):
            return {"game_over": True}

        if keysym in ("Caps_Lock"):
            return {"ignored": True}

        if keysym == "BackSpace":
            if self.char_index > 0:
                self.char_index -= 1
                return {"action": "backspace", "index": self.char_index}
            else:
                return {"ignored": True}

        if len(char) == 1 and ord(char) >= 32:
            idx = self.char_index
            correct_char = self.current_text[self.char_index] if self.char_index < len(self.current_text) else None
            is_correct = (char == correct_char)
            if not is_correct:
                self.mistakes += 1
            self.char_index += 1
            game_over = self.char_index >= len(self.current_text)
            return {"action": "key_press", "index": idx, "correct": is_correct, "game_over": game_over}

        return {"ignored": True}

    def update_timer(self):
        self.time_left -= 1 if self.game_mode == "time" else -1

    def get_stats(self):
        time_elapsed = (self.max_time - self.time_left) if self.game_mode == "time" else self.time_left
        if time_elapsed > 0:
            cpm = round(((self.char_index - self.mistakes) / time_elapsed) * 60)
            wpm = round(cpm / 5)
        else:
            wpm = cpm = 0
        return {"WPM": max(0, wpm), "CPM": max(0, cpm), "Mistakes": self.mistakes, "TimeLeft": self.time_left}

    def is_game_over(self):
        return (self.time_left <= 0 if self.game_mode == "time" else self.char_index >= len(self.current_text))
