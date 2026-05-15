import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DATA_FILE = 'expenses.json'

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.expenses = []

        # Загружаем данные
        self.load_data()

        # Создаем интерфейс
        self.create_widgets()
        self.refresh_treeview()

    def create_widgets(self):
        # Поля ввода
        tk.Label(self.root, text="Сумма").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Категория").grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar()
        categories = ['Еда', 'Транспорт', 'Развлечения', 'Другое']
        self.category_menu = ttk.OptionMenu(self.root, self.category_var, categories[0], *categories)
        self.category_menu.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(self.root, text="Дата (YYYY-MM-DD)").grid(row=0, column=4, padx=5, pady=5)
        self.date_entry = tk.Entry(self.root)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

        # Кнопка добавить расход
        self.add_button = tk.Button(self.root, text="Добавить расход", command=self.add_expense)
        self.add_button.grid(row=0, column=6, padx=5, pady=5)

        # Фильтры
        tk.Label(self.root, text="Фильтр по категории").grid(row=1, column=0, padx=5, pady=5)
        self.filter_category_var = tk.StringVar()
        categories_filter = ['Все'] + categories
        self.filter_category_menu = ttk.OptionMenu(self.root, self.filter_category_var, 'Все', *categories_filter, command=self.apply_filters)
        self.filter_category_menu.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Фильтр по дате (YYYY-MM-DD)").grid(row=1, column=2, padx=5, pady=5)
        self.filter_date_entry = tk.Entry(self.root)
        self.filter_date_entry.grid(row=1, column=3, padx=5, pady=5)
        self.filter_date_entry.bind("<KeyRelease>", lambda e: self.apply_filters())

        self.clear_filter_button = tk.Button(self.root, text="Сбросить фильтр", command=self.reset_filters)
        self.clear_filter_button.grid(row=1, column=4, padx=5, pady=5)

        # Таблица расходов
        columns = ('amount', 'category', 'date')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')
        self.tree.heading('amount', text='Сумма')
        self.tree.heading('category', text='Категория')
        self.tree.heading('date', text='Дата')
        self.tree.grid(row=2, column=0, columnspan=7, padx=5, pady=5)

        # Общая сумма
        self.total_label = tk.Label(self.root, text="Общая сумма: 0")
        self.total_label.grid(row=3, column=0, padx=5, pady=5, sticky='w')

    def load_data(self):
        try:
            with open(DATA_FILE, 'r') as f:
                self.expenses = json.load(f)
        except FileNotFoundError:
            self.expenses = []

    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.expenses, f, indent=4)

    def add_expense(self):
        amount_str = self.amount_entry.get()
        category = self.category_var.get()
        date_str = self.date_entry.get()

        # Проверка введенных данных
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите положительное число для суммы.")
            return

        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Ошибка", "Введите дату в формате ГГГГ-ММ-ДД.")
            return

        new_expense = {
            'amount': amount,
            'category': category,
            'date': date_str
        }
        self.expenses.append(new_expense)
        self.save_data()
        self.refresh_treeview()
        self.clear_entries()

    def clear_entries(self):
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

    def refresh_treeview(self, filtered_expenses=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        expenses_to_show = filtered_expenses if filtered_expenses is not None else self.expenses
        total = 0
        for exp in expenses_to_show:
            self.tree.insert('', tk.END, values=(exp['amount'], exp['category'], exp['date']))
            total += exp['amount']
        self.total_label.config(text=f"Общая сумма: {total:.2f}")

    def apply_filters(self):
        category_filter = self.filter_category_var.get()
        date_filter = self.filter_date_entry.get()

        filtered = self.expenses
        if category_filter != 'Все':
            filtered = [exp for exp in filtered if exp['category'] == category_filter]
        if date_filter:
            try:
                datetime.strptime(date_filter, '%Y-%m-%d')
                filtered = [exp for exp in filtered if exp['date'] == date_filter]
            except ValueError:
                pass  # некорректный формат, игнорируем

        self.refresh_treeview(filtered)

    def reset_filters(self):
        self.filter_category_var.set('Все')
        self.filter_date_entry.delete(0, tk.END)
        self.refresh_treeview()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
