import tkinter as tk
from tkinter import messagebox
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import speech_recognition as sr
import random
import os
import threading # Для работы с аудио в отдельном потоке
import time

# --- 1. Словарь: Русское слово -> Ожидаемый английский перевод ---
WORD_PAIRS = {
    "привет": "hello", "мир": "world", "солнце": "sun", "книга": "book", "компьютер": "computer",
    "программа": "program", "язык": "language", "друг": "friend", "кошка": "cat", "собака": "dog",
    "дом": "house", "машина": "car", "дорога": "road", "небо": "sky", "облако": "cloud",
    "река": "river", "лес": "forest", "гора": "mountain", "поле": "field", "город": "city",
    "ветер": "wind", "дождь": "rain", "снег": "snow", "тепло": "warm", "холод": "cold",
    "счастье": "happiness", "радость": "joy", "yacht": "yacht", "любовь": "love", "работа": "work", # yacht для проверки различий в произношении
    "время": "time", "день": "day", "ночь": "night", "утро": "morning", "вечер": "evening",
    "завтрак": "breakfast", "обед": "lunch", "ужин": "dinner", "вода": "water", "огонь": "fire",
    "земля": "earth", "воздух": "air", "человек": "person", "жизнь": "life", "смерть": "death",
    "начало": "start", "конец": "end", "вопрос": "question", "ответ": "answer", "тишина": "silence",
    "звук": "sound", "музыка": "music", "песня": "song", "танец": "dance", "бежать": "run",
    "идти": "walk", "спать": "sleep", "есть": "eat", "пить": "drink", "говорить": "speak",
    "читать": "read", "писать": "write", "думать": "think", "знать": "know", "хотеть": "want",
    "мочь": "can", "делать": "do", "видеть": "see", "слышать": "hear", "чувствовать": "feel",
    "большой": "big", "маленький": "small", "красивый": "beautiful", "новый": "new", "старый": "old",
    "хороший": "good", "плохой": "bad", "быстрый": "fast", "медленный": "slow", "легкий": "easy",
    "тяжелый": "hard", "свет": "light", "тень": "shadow", "красный": "red", "синий": "blue",
    "зеленый": "green", "желтый": "yellow", "белый": "white", "черный": "black", "здоровье": "health",
    "успех": "success", "дождь": "rain", "снег": "snow", "зима": "winter", "лето": "summer",
    "осень": "autumn", "весна": "spring", "семья": "family", "школа": "school", "учитель": "teacher",
    "ученик": "student", "доктор": "doctor", "инженер": "engineer", "политик": "politician",
    "музыкант": "musician", "художник": "artist", "писатель": "writer", "актер": "actor",
    "спортсмен": "athlete", "король": "king", "королева": "queen", "принц": "prince", "принцесса": "princess"
}

# Проверяем, что у нас есть слова для игры
if len(WORD_PAIRS) < 100:
    print(f"Внимание: В словаре {len(WORD_PAIRS)} пар. Для полноценной игры рекомендуется 100.")

# --- 2. Настройки записи и распознавания ---
DURATION_SECONDS = 3
SAMPLE_RATE = 44100
OUTPUT_FILENAME = "output_temp_audio.wav"

recognizer = sr.Recognizer()

# --- 3. Класс для GUI приложения ---
class PronunciationApp:
    def __init__(self, master):
        self.master = master
        master.title(" Произношение слов: Русский -> Английский")
        master.geometry("700x700") # Размер окна

        self.current_russian_word = ""
        self.current_english_word = ""

        # --- Элементы GUI ---
        self.title_label = tk.Label(master, text="Скажи английский перевод!", font=("Helvetica", 30, "bold"))
        self.title_label.pack(pady=20)

        self.russian_word_label = tk.Label(master, text="Нажми 'Начать', чтобы получить слово...", font=("Helvetica", 16))
        self.russian_word_label.pack(pady=10)

        self.prompt_label = tk.Label(master, text="Приготовься говорить...", font=("Helvetica", 12), fg="gray")
        self.prompt_label.pack(pady=5)
        
        self.recognized_label = tk.Label(master, text="Распознано: ", font=("Helvetica", 12), fg="blue")
        self.recognized_label.pack(pady=5)

        self.result_label = tk.Label(master, text="", font=("Helvetica", 14, "bold"), wraplength=400) # wraplength для переноса длинного текста
        self.result_label.pack(pady=10)

        # Кнопки
        self.start_button = tk.Button(master, text="Начать раунд", command=self.start_round_thread, font=("Helvetica", 12))
        self.start_button.pack(pady=5)

        self.repeat_button = tk.Button(master, text="Повторить", command=self.start_round_thread, font=("Helvetica", 12), state=tk.DISABLED)
        self.repeat_button.pack(pady=5)
        
        self.exit_button = tk.Button(master, text="Выход", command=master.quit, font=("Helvetica", 12))
        self.exit_button.pack(pady=5)

        # Статус индикатор (например, "Запись...", "Распознавание...")
        self.status_label = tk.Label(master, text="", font=("Helvetica", 10), fg="purple")
        self.status_label.pack(pady=5)
        
        if not WORD_PAIRS:
            messagebox.showerror("Ошибка", "Словарь пуст! Невозможно начать игру.")
            self.start_button.config(state=tk.DISABLED)
            self.repeat_button.config(state=tk.DISABLED)

    def set_gui_state(self, recording=False, recognizing=False):
        """Управляет состоянием кнопок и статусной строки."""
        if recording or recognizing:
            self.start_button.config(state=tk.DISABLED)
            self.repeat_button.config(state=tk.DISABLED)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.repeat_button.config(state=tk.NORMAL)

    def start_round_thread(self):
        """Запускает новый раунд в отдельном потоке."""
        # Обнуляем предыдущие результаты
        self.recognized_label.config(text="Распознано: ", fg="blue")
        self.result_label.config(text="", fg="black")
        
        threading.Thread(target=self._run_round_logic, daemon=True).start()

    def _run_round_logic(self):
        """Логика одного раунда игры (выбор слова, запись, распознавание, проверка)."""
        self.set_gui_state(recording=True) # Блокируем кнопки
        
        # 1. Выбираем слово
        russian_words = list(WORD_PAIRS.keys())
        if not russian_words:
            self.master.after(0, lambda: messagebox.showerror("Ошибка", "Словарь пуст!"))
            self.set_gui_state(recording=False)
            return

        self.current_russian_word = random.choice(russian_words)
        self.current_english_word = WORD_PAIRS[self.current_russian_word]
        
        self.master.after(0, lambda: self.russian_word_label.config(
            text=f"Русское слово: \"{self.current_russian_word}\""))
        self.master.after(0, lambda: self.prompt_label.config(
            text="Пожалуйста, скажи его английский перевод:", fg="black"))

        # 2. Запись звука
        try:
            time.sleep(0.5) # Пауза перед записью
            recording = sd.rec(
                int(DURATION_SECONDS * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="int16")
            sd.wait()
            
            # Сохраняем запись во временный файл
            wav.write(OUTPUT_FILENAME, SAMPLE_RATE, recording)

        except Exception as e:
            self.master.after(0, lambda: self.result_label.config(
                text=f"❌ Ошибка при записи аудио: {e}", fg="red"))
            self.set_gui_state(recording=False)
            return
        
        self.set_gui_state(recognizing=True) # Обновляем статус
        
        # 3. Распознавание произнесенного слова
        user_text = None
        if not os.path.exists(OUTPUT_FILENAME):
            self.master.after(0, lambda: self.result_label.config(
                text=f"Ошибка: Временный файл '{OUTPUT_FILENAME}' не был создан.", fg="red"))
        else:
            with sr.AudioFile(OUTPUT_FILENAME) as source:
                try:
                    audio = recognizer.record(source)
                    user_text = recognizer.recognize_google(audio, language="en-US")
                    self.master.after(0, lambda: self.recognized_label.config(
                        text=f"Распознано: {user_text}", fg="blue"))
                except sr.UnknownValueError:
                    self.master.after(0, lambda: self.result_label.config(
                        text="😔 Google не смог распознать, что ты сказал. Попробуй еще раз.", fg="orange"))
                except sr.RequestError as e:
                    self.master.after(0, lambda: self.result_label.config(
                        text=f"🌐 Ошибка сервиса Google (проверь интернет): {e}", fg="red"))
                except Exception as e:
                    self.master.after(0, lambda: self.result_label.config(
                        text=f"❌ Произошла другая ошибка при распознавании: {e}", fg="red"))
            
            # Удаляем временный файл после использования
            try:
                os.remove(OUTPUT_FILENAME)
            except OSError as e:
                print(f"Ошибка при удалении временного файла '{OUTPUT_FILENAME}': {e}") # Выводим в консоль, не критично для GUI

        # 4. Сравнение с ожидаемым английским словом
        if user_text:
            if user_text.lower().strip() == self.current_english_word.lower():
                self.master.after(0, lambda: self.result_label.config(
                    text=f"✅ ОТЛИЧНО! Ты правильно сказал \"{self.current_english_word}\". ✅", fg="green"))
            else:
                self.master.after(0, lambda: self.result_label.config(
                    text=f"❌ Не совсем. Ты сказал '{user_text}', а нужно было \"{self.current_english_word}\".", fg="red"))
        else:
            if not self.result_label.cget("text"): # Если ошибка распознавания не была установлена ранее
                 self.master.after(0, lambda: self.result_label.config(
                    text="😕 Не удалось распознать твою речь. Попробуй сказать четче!", fg="orange"))
        
        self.set_gui_state(recording=False) # Разблокируем кнопки

# --- Запуск приложения ---
if __name__ == "__main__":

    root = tk.Tk()
    app = PronunciationApp(root)
    root.mainloop()
