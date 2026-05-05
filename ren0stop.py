import random
import string
import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox


class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # Файл истории
        self.history_file = "history.json"
        self.history = self.load_history()

        # Создание интерфейса
        self.create_widgets()

        # Загрузка истории в таблицу
        self.update_history_table()

    def create_widgets(self):
        # Рамка настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Ползунок длины пароля
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w", pady=5)
        self.length_var = tk.IntVar(value=12)
        self.length_slider = ttk.Scale(settings_frame, from_=4, to=32, orient="horizontal",
                                       variable=self.length_var, command=self.update_length_label)
        self.length_slider.grid(row=0, column=1, padx=10, sticky="ew", pady=5)

        self.length_label = ttk.Label(settings_frame, text="12")
        self.length_label.grid(row=0, column=2, padx=5)

        # Чекбоксы выбора символов
        self.use_digits = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w",
                                                                                           pady=5)

        self.use_letters = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Буквы (A-Z, a-z)", variable=self.use_letters).grid(row=1, column=1,
                                                                                                 sticky="w", pady=5)

        self.use_symbols = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&*_+)", variable=self.use_symbols).grid(row=1,
                                                                                                         column=2,
                                                                                                         sticky="w",
                                                                                                         pady=5)

        # Кнопка генерации
        generate_btn = ttk.Button(settings_frame, text="Сгенерировать пароль", command=self.generate_password)
        generate_btn.grid(row=2, column=0, columnspan=3, pady=10)

        # Поле для отображения сгенерированного пароля
        ttk.Label(settings_frame, text="Сгенерированный пароль:").grid(row=3, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(settings_frame, textvariable=self.password_var, font=("Courier", 12), width=40)
        self.password_entry.grid(row=3, column=1, columnspan=2, sticky="ew", pady=5)

        # Кнопка копирования
        copy_btn = ttk.Button(settings_frame, text="Копировать", command=self.copy_to_clipboard)
        copy_btn.grid(row=4, column=1, columnspan=2, pady=5)

        # Рамка истории
        history_frame = ttk.LabelFrame(self.root, text="История паролей", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Таблица истории
        columns = ("timestamp", "length", "char_types", "password")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)

        self.history_tree.heading("timestamp", text="Дата и время")
        self.history_tree.heading("length", text="Длина")
        self.history_tree.heading("char_types", text="Типы символов")
        self.history_tree.heading("password", text="Пароль")

        self.history_tree.column("timestamp", width=150)
        self.history_tree.column("length", width=60)
        self.history_tree.column("char_types", width=120)
        self.history_tree.column("password", width=200)

        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления историей
        history_buttons_frame = ttk.Frame(history_frame)
        history_buttons_frame.pack(fill="x", pady=5)

        ttk.Button(history_buttons_frame, text="Очистить историю", command=self.clear_history).pack(side="left", padx=5)
        ttk.Button(history_buttons_frame, text="Обновить", command=self.update_history_table).pack(side="left", padx=5)

        # Настройка весов для адаптивности
        settings_frame.columnconfigure(1, weight=1)

    def update_length_label(self, event=None):
        self.length_label.config(text=str(int(self.length_var.get())))

    def get_char_pool(self):
        char_pool = ""

        if self.use_letters.get():
            char_pool += string.ascii_letters
        if self.use_digits.get():
            char_pool += string.digits
        if self.use_symbols.get():
            char_pool += "!@#$%^&*_+"

        return char_pool

    def validate_settings(self):
        length = int(self.length_var.get())

        # Проверка длины
        if length < 4:
            messagebox.showerror("Ошибка", "Минимальная длина пароля - 4 символа")
            return False
        if length > 32:
            messagebox.showerror("Ошибка", "Максимальная длина пароля - 32 символа")
            return False

        # Проверка выбора символов
        char_pool = self.get_char_pool()
        if not char_pool:
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов")
            return False

        return True

    def generate_password(self):
        if not self.validate_settings():
            return

        length = int(self.length_var.get())
        char_pool = self.get_char_pool()

        # Генерация пароля
        password = ''.join(random.choice(char_pool) for _ in range(length))

        # Отображение
        self.password_var.set(password)

        # Сохранение в историю
        self.save_to_history(password, length)

    def save_to_history(self, password, length):
        # Определение типов символов
        char_types = []
        if self.use_letters.get():
            char_types.append("буквы")
        if self.use_digits.get():
            char_types.append("цифры")
        if self.use_symbols.get():
            char_types.append("спецсимволы")

        char_types_str = ", ".join(char_types)

        # Создание записи
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "length": length,
            "char_types": char_types_str,
            "password": password
        }

        # Добавление в историю
        self.history.insert(0, entry)  # Новые записи в начало
        self.save_history()
        self.update_history_table()

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")

    def update_history_table(self):
        # Очистка таблицы
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Заполнение таблицы
        for entry in self.history:
            self.history_tree.insert("", "end", values=(
                entry["timestamp"],
                entry["length"],
                entry["char_types"],
                entry["password"]
            ))

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.update_history_table()
            self.password_var.set("")

    def copy_to_clipboard(self):
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Внимание", "Нет пароля для копирования")


def main():
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()