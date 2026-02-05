"""
Графический интерфейс приложения на Tkinter
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from datetime import datetime
import threading

from database.database_handler import PostgreSQLHandler, setup_database, create_test_data


class MainWindow:
    """Главное окно приложения на Tkinter"""

    def __init__(self, root):
        self.root = root
        self.root.title("Desktop App with PostgreSQL (pg8000)")
        self.root.geometry("1200x700")

        # Инициализируем обработчик БД
        self.db_handler = PostgreSQLHandler()

        # Создание интерфейса
        self.create_widgets()

        # Загрузка данных
        self.load_data_threaded()

    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Основной контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Заголовок
        title_label = ttk.Label(
            main_container,
            text="📊 Управление базой данных PostgreSQL",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 10))

        # Статус подключения
        self.status_label = ttk.Label(
            main_container,
            text="Проверка подключения...",
            font=('Arial', 10)
        )
        self.status_label.pack(pady=(0, 10))
        self.update_status_label()

        # Notebook (вкладки)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Создаем вкладки
        self.create_customers_tab()
        self.create_products_tab()
        self.create_orders_tab()
        self.create_statistics_tab()

        # Панель кнопок
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            button_frame,
            text="🔄 Обновить данные",
            command=self.load_data_threaded
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="⚙️ Настроить БД",
            command=self.setup_database
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="🧪 Тест подключения",
            command=self.test_connection
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="📝 Тестовые данные",
            command=self.create_test_data
        ).pack(side=tk.LEFT, padx=5)

        # Прогресс бар
        self.progress = ttk.Progressbar(
            button_frame,
            mode='indeterminate',
            length=100
        )
        self.progress.pack(side=tk.RIGHT, padx=5)

    def create_customers_tab(self):
        """Вкладка клиентов"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="👥 Клиенты")

        # Панель с разделителем
        paned = ttk.PanedWindow(tab, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Форма добавления клиента
        form_frame = ttk.LabelFrame(paned, text="Добавить нового клиента", padding=10)

        # Поля формы
        fields = ttk.Frame(form_frame)
        fields.pack(fill=tk.X, expand=True)

        ttk.Label(fields, text="Имя:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.first_name_entry = ttk.Entry(fields, width=30)
        self.first_name_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(fields, text="Фамилия:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.last_name_entry = ttk.Entry(fields, width=30)
        self.last_name_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(fields, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.email_entry = ttk.Entry(fields, width=30)
        self.email_entry.grid(row=2, column=1, pady=5, padx=5)

        ttk.Label(fields, text="Телефон:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        self.phone_entry = ttk.Entry(fields, width=30)
        self.phone_entry.grid(row=3, column=1, pady=5, padx=5)

        ttk.Label(fields, text="Адрес:").grid(row=4, column=0, sticky=tk.NW, pady=5, padx=5)
        self.address_text = scrolledtext.ScrolledText(fields, width=30, height=3)
        self.address_text.grid(row=4, column=1, pady=5, padx=5)

        # Кнопка добавления
        ttk.Button(
            form_frame,
            text="➕ Добавить клиента",
            command=self.add_customer
        ).pack(pady=(10, 0))

        paned.add(form_frame)

        # Таблица клиентов
        table_frame = ttk.Frame(paned)

        # Создаем Treeview
        columns = ("ID", "Имя", "Фамилия", "Email", "Телефон", "Дата создания")
        self.customers_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Настройка колонок
        for col in columns:
            self.customers_tree.heading(col, text=col)
            self.customers_tree.column(col, width=100)

        # Прокрутка
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=scrollbar.set)

        self.customers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        paned.add(table_frame)

    def create_products_tab(self):
        """Вкладка товаров"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📦 Товары")

        paned = ttk.PanedWindow(tab, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Форма добавления товара
        form_frame = ttk.LabelFrame(paned, text="Добавить новый товар", padding=10)

        fields = ttk.Frame(form_frame)
        fields.pack(fill=tk.X, expand=True)

        ttk.Label(fields, text="Наименование:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.product_name_entry = ttk.Entry(fields, width=30)
        self.product_name_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(fields, text="Артикул:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.product_sku_entry = ttk.Entry(fields, width=30)
        self.product_sku_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(fields, text="Категория:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.product_category_combo = ttk.Combobox(
            fields,
            values=["electronics", "clothing", "books", "food", "other"],
            width=27,
            state="readonly"
        )
        self.product_category_combo.grid(row=2, column=1, pady=5, padx=5)
        self.product_category_combo.current(4)

        ttk.Label(fields, text="Цена:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        self.product_price_spinbox = tk.Spinbox(
            fields,
            from_=0,
            to=1000000,
            increment=1,
            width=27
        )
        self.product_price_spinbox.grid(row=3, column=1, pady=5, padx=5)

        ttk.Label(fields, text="Количество:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=5)
        self.product_quantity_spinbox = tk.Spinbox(
            fields,
            from_=0,
            to=10000,
            increment=1,
            width=27
        )
        self.product_quantity_spinbox.grid(row=4, column=1, pady=5, padx=5)

        ttk.Label(fields, text="Описание:").grid(row=5, column=0, sticky=tk.NW, pady=5, padx=5)
        self.product_description_text = scrolledtext.ScrolledText(fields, width=30, height=3)
        self.product_description_text.grid(row=5, column=1, pady=5, padx=5)

        ttk.Button(
            form_frame,
            text="➕ Добавить товар",
            command=self.add_product
        ).pack(pady=(10, 0))

        paned.add(form_frame)

        # Таблица товаров
        table_frame = ttk.Frame(paned)

        columns = ("ID", "Наименование", "Артикул", "Категория", "Цена", "Количество", "Статус")
        self.products_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)

        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        paned.add(table_frame)

    def create_orders_tab(self):
        """Вкладка заказов"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📋 Заказы")

        paned = ttk.PanedWindow(tab, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Форма создания заказа
        form_frame = ttk.LabelFrame(paned, text="Создать новый заказ", padding=10)

        fields = ttk.Frame(form_frame)
        fields.pack(fill=tk.X, expand=True)

        ttk.Label(fields, text="Клиент:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.order_customer_combo = ttk.Combobox(fields, width=27, state="readonly")
        self.order_customer_combo.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(fields, text="Примечания:").grid(row=1, column=0, sticky=tk.NW, pady=5, padx=5)
        self.order_notes_text = scrolledtext.ScrolledText(fields, width=30, height=3)
        self.order_notes_text.grid(row=1, column=1, pady=5, padx=5)

        ttk.Button(
            form_frame,
            text="📝 Создать заказ",
            command=self.create_order_dialog
        ).pack(pady=(10, 0))

        paned.add(form_frame)

        # Таблица заказов
        table_frame = ttk.Frame(paned)

        columns = ("ID", "Клиент", "Дата заказа", "Статус", "Сумма", "Примечания")
        self.orders_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=100)

        # Контекстное меню
        self.order_context_menu = tk.Menu(self.root, tearoff=0)
        self.order_context_menu.add_command(label="Изменить статус", command=self.change_order_status)
        self.order_context_menu.add_command(label="Показать детали", command=self.show_order_details)

        self.orders_tree.bind("<Button-3>", self.show_context_menu)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)

        self.orders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        paned.add(table_frame)

    def create_statistics_tab(self):
        """Вкладка статистики"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📈 Статистика")

        main_frame = ttk.Frame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Статистика
        stats_frame = ttk.LabelFrame(main_frame, text="Статистика базы данных", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        self.stats_text = tk.Text(stats_frame, height=8, font=('Arial', 10))
        self.stats_text.pack(fill=tk.BOTH, expand=True)

        # Произвольный запрос
        query_frame = ttk.LabelFrame(main_frame, text="Произвольный SQL запрос", padding=10)
        query_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(query_frame, text="Введите SQL запрос:").pack(anchor=tk.W)
        self.query_text = scrolledtext.ScrolledText(query_frame, height=4, font=('Courier', 10))
        self.query_text.pack(fill=tk.X, pady=(5, 5))

        ttk.Button(
            query_frame,
            text="▶️ Выполнить запрос",
            command=self.execute_custom_query
        ).pack()

        # Результаты запроса
        result_frame = ttk.LabelFrame(main_frame, text="Результаты запроса", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview для результатов
        self.query_result_tree = ttk.Treeview(result_frame, show="headings", height=10)

        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.query_result_tree.yview)
        self.query_result_tree.configure(yscrollcommand=scrollbar.set)

        self.query_result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def update_status_label(self):
        """Обновление статуса подключения"""
        if self.db_handler.check_connection():
            self.status_label.config(text="✅ Подключено к PostgreSQL", foreground='green')
        else:
            self.status_label.config(text="❌ Нет подключения к базе данных", foreground='red')

    def load_data_threaded(self):
        """Загрузка данных в отдельном потоке"""
        self.progress.start()
        self.root.config(cursor="watch")

        thread = threading.Thread(target=self.load_data)
        thread.daemon = True
        thread.start()

        # Проверка завершения
        self.check_thread_completion(thread)

    def load_data(self):
        """Загрузка данных из базы"""
        try:
            # Загрузка клиентов
            from database.models import Customer
            customers = Customer.objects.all()

            # Обновляем в основном потоке
            self.root.after(0, self.update_customers_table, customers)

            # Загрузка товаров
            from database.models import Product
            products = Product.objects.all()
            self.root.after(0, self.update_products_table, products)

            # Обновление комбобокса клиентов
            customer_data = [(f"{c.id}: {c.last_name} {c.first_name}", c.id) for c in customers]
            self.root.after(0, self.update_customer_combo, customer_data)

            # Загрузка заказов
            from database.models import Order
            orders = Order.objects.select_related('customer').all()
            self.root.after(0, self.update_orders_table, orders)

            # Статистика
            stats = self.db_handler.get_database_stats()
            self.root.after(0, self.update_statistics, stats)

        except Exception as e:
            self.root.after(0, self.show_error, "Ошибка загрузки данных", str(e))

    def check_thread_completion(self, thread):
        """Проверка завершения потока"""
        if thread.is_alive():
            self.root.after(100, self.check_thread_completion, thread)
        else:
            self.root.config(cursor="")
            self.progress.stop()

    def update_customers_table(self, customers):
        """Обновление таблицы клиентов"""
        # Очищаем таблицу
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)

        # Добавляем данные
        for customer in customers:
            self.customers_tree.insert("", tk.END, values=(
                customer.id,
                customer.first_name,
                customer.last_name,
                customer.email,
                customer.phone,
                customer.created_at.strftime("%Y-%m-%d %H:%M")
            ))

    def update_products_table(self, products):
        """Обновление таблицы товаров"""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        for product in products:
            self.products_tree.insert("", tk.END, values=(
                product.id,
                product.name,
                product.sku,
                product.get_category_display(),
                f"₽{product.price}",
                product.quantity,
                "✅ Активен" if product.is_active else "❌ Не активен"
            ))

    def update_customer_combo(self, customer_data):
        """Обновление комбобокса клиентов"""
        self.order_customer_combo['values'] = [item[0] for item in customer_data]
        if customer_data:
            self.order_customer_combo.current(0)

    def update_orders_table(self, orders):
        """Обновление таблицы заказов"""
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        for order in orders:
            self.orders_tree.insert("", tk.END, values=(
                order.id,
                str(order.customer),
                order.order_date.strftime("%Y-%m-%d %H:%M"),
                order.get_status_display(),
                f"₽{order.total_amount}",
                order.notes[:50] + "..." if len(order.notes) > 50 else order.notes
            ), tags=(order.status,))

    def update_statistics(self, stats):
        """Обновление статистики"""
        stats_text = f"""
📊 Статистика базы данных:

👥 Клиенты: {stats.get('customers', 0)}
📦 Всего товаров: {stats.get('products', 0)} (активных: {stats.get('active_products', 0)})
📋 Всего заказов: {stats.get('orders', 0)}
⏳ Заказов в обработке: {stats.get('pending_orders', 0)}

Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)

    def add_customer(self):
        """Добавление нового клиента"""
        try:
            # Проверяем обязательные поля
            if not self.first_name_entry.get() or not self.last_name_entry.get() or not self.email_entry.get():
                messagebox.showwarning("Ошибка", "Заполните обязательные поля: Имя, Фамилия, Email")
                return

            customer = self.db_handler.create_customer(
                first_name=self.first_name_entry.get(),
                last_name=self.last_name_entry.get(),
                email=self.email_entry.get(),
                phone=self.phone_entry.get(),
                address=self.address_text.get(1.0, tk.END).strip()
            )

            if customer:
                messagebox.showinfo("Успех", f"Клиент {customer.first_name} {customer.last_name} успешно добавлен!")
                self.clear_customer_form()
                self.load_data_threaded()
            else:
                messagebox.showwarning("Ошибка", "Не удалось добавить клиента. Возможно, email уже существует.")

        except Exception as e:
            self.show_error("Ошибка при добавлении клиента", str(e))

    def add_product(self):
        """Добавление нового товара"""
        try:
            # Проверяем обязательные поля
            if not self.product_name_entry.get() or not self.product_sku_entry.get():
                messagebox.showwarning("Ошибка", "Заполните обязательные поля: Наименование и Артикул")
                return

            product = self.db_handler.create_product(
                name=self.product_name_entry.get(),
                sku=self.product_sku_entry.get(),
                category=self.product_category_combo.get(),
                price=float(self.product_price_spinbox.get()),
                quantity=int(self.product_quantity_spinbox.get()),
                description=self.product_description_text.get(1.0, tk.END).strip()
            )

            if product:
                messagebox.showinfo("Успех", f"Товар {product.name} успешно добавлен!")
                self.clear_product_form()
                self.load_data_threaded()
            else:
                messagebox.showwarning("Ошибка", "Не удалось добавить товар. Возможно, артикул уже существует.")

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")
        except Exception as e:
            self.show_error("Ошибка при добавлении товара", str(e))

    def create_order_dialog(self):
        """Диалог создания заказа"""
        try:
            customer_selection = self.order_customer_combo.get()
            if not customer_selection:
                messagebox.showwarning("Ошибка", "Выберите клиента")
                return

            # Создаем диалоговое окно для выбора товаров
            dialog = tk.Toplevel(self.root)
            dialog.title("Создание заказа")
            dialog.geometry("800x600")
            dialog.transient(self.root)
            dialog.grab_set()

            # Получаем доступные товары
            from database.models import Product
            products = Product.objects.filter(is_active=True, quantity__gt=0)

            # Создаем интерфейс для выбора товаров
            ttk.Label(dialog, text="Выберите товары для заказа:", font=('Arial', 12, 'bold')).pack(pady=10)

            # Фрейм для товаров
            products_frame = ttk.Frame(dialog)
            products_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Заголовки
            headers_frame = ttk.Frame(products_frame)
            headers_frame.pack(fill=tk.X)

            ttk.Label(headers_frame, text="Товар", width=30).pack(side=tk.LEFT, padx=5)
            ttk.Label(headers_frame, text="Цена", width=10).pack(side=tk.LEFT, padx=5)
            ttk.Label(headers_frame, text="На складе", width=10).pack(side=tk.LEFT, padx=5)
            ttk.Label(headers_frame, text="Кол-во", width=10).pack(side=tk.LEFT, padx=5)

            # Список товаров
            self.order_items = {}
            for product in products:
                item_frame = ttk.Frame(products_frame)
                item_frame.pack(fill=tk.X, pady=2)

                ttk.Label(item_frame, text=product.name, width=30).pack(side=tk.LEFT, padx=5)
                ttk.Label(item_frame, text=f"₽{product.price}", width=10).pack(side=tk.LEFT, padx=5)
                ttk.Label(item_frame, text=str(product.quantity), width=10).pack(side=tk.LEFT, padx=5)

                # Поле для ввода количества
                quantity_var = tk.StringVar(value="0")
                quantity_entry = ttk.Entry(item_frame, textvariable=quantity_var, width=10)
                quantity_entry.pack(side=tk.LEFT, padx=5)

                self.order_items[product.id] = {
                    'product': product,
                    'quantity_var': quantity_var,
                    'entry': quantity_entry
                }

            # Кнопки
            buttons_frame = ttk.Frame(dialog)
            buttons_frame.pack(fill=tk.X, pady=10)

            ttk.Button(
                buttons_frame,
                text="✅ Создать заказ",
                command=lambda: self.create_order_from_dialog(dialog, customer_selection)
            ).pack(side=tk.LEFT, padx=20)

            ttk.Button(
                buttons_frame,
                text="❌ Отмена",
                command=dialog.destroy
            ).pack(side=tk.RIGHT, padx=20)

        except Exception as e:
            self.show_error("Ошибка при создании заказа", str(e))

    def create_order_from_dialog(self, dialog, customer_selection):
        """Создание заказа из диалога"""
        try:
            # Извлекаем ID клиента
            customer_id = int(customer_selection.split(":")[0])

            # Собираем товары
            items = []
            for product_id, item_data in self.order_items.items():
                try:
                    quantity = int(item_data['quantity_var'].get())
                    if quantity > 0:
                        items.append({
                            'product_id': product_id,
                            'quantity': quantity
                        })
                except ValueError:
                    continue

            if not items:
                messagebox.showwarning("Ошибка", "Выберите хотя бы один товар")
                return

            # Создаем заказ
            order = self.db_handler.create_order(
                customer_id=customer_id,
                items=items,
                notes=self.order_notes_text.get(1.0, tk.END).strip()
            )

            if order:
                messagebox.showinfo("Успех", f"Заказ #{order.id} успешно создан!")
                dialog.destroy()
                self.load_data_threaded()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать заказ")

        except Exception as e:
            self.show_error("Ошибка при создании заказа", str(e))

    def show_context_menu(self, event):
        """Показать контекстное меню"""
        item = self.orders_tree.identify_row(event.y)
        if item:
            self.selected_order_item = item
            self.order_context_menu.post(event.x_root, event.y_root)

    def change_order_status(self):
        """Изменение статуса заказа"""
        if not hasattr(self, 'selected_order_item'):
            return

        try:
            order_id = self.orders_tree.item(self.selected_order_item)['values'][0]

            # Диалог выбора статуса
            new_status = simpledialog.askstring(
                "Изменение статуса",
                f"Введите новый статус для заказа #{order_id}:\n"
                "(pending, processing, shipped, delivered, cancelled)",
                parent=self.root
            )

            if new_status and new_status in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
                if self.db_handler.update_order_status(order_id, new_status):
                    messagebox.showinfo("Успех", "Статус заказа обновлен!")
                    self.load_data_threaded()
                else:
                    messagebox.showerror("Ошибка", "Не удалось обновить статус")
            elif new_status:
                messagebox.showwarning("Ошибка", "Некорректный статус")

        except Exception as e:
            self.show_error("Ошибка при изменении статуса", str(e))

    def show_order_details(self):
        """Показать детали заказа"""
        if not hasattr(self, 'selected_order_item'):
            return

        try:
            order_id = self.orders_tree.item(self.selected_order_item)['values'][0]

            from database.models import Order, OrderItem
            order = Order.objects.get(id=order_id)
            items = OrderItem.objects.filter(order=order).select_related('product')

            dialog = tk.Toplevel(self.root)
            dialog.title(f"Детали заказа #{order_id}")
            dialog.geometry("600x500")

            text = scrolledtext.ScrolledText(dialog, font=('Arial', 10))
            text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            details = f"""
Заказ #{order.id}
Клиент: {order.customer}
Дата заказа: {order.order_date.strftime('%Y-%m-%d %H:%M')}
Статус: {order.get_status_display()}
Общая сумма: ₽{order.total_amount}
Примечания: {order.notes}

Товары в заказе:
{'-' * 50}
"""

            total = 0
            for item in items:
                details += f"\n{item.product.name} x{item.quantity} = ₽{item.total_price}"
                total += float(item.total_price)

            details += f"\n{'-' * 50}"
            details += f"\nИтого: ₽{total}"

            text.insert(1.0, details)
            text.config(state=tk.DISABLED)

        except Exception as e:
            self.show_error("Ошибка при получении деталей заказа", str(e))

    def execute_custom_query(self):
        """Выполнение произвольного SQL запроса"""
        try:
            query = self.query_text.get(1.0, tk.END).strip()
            if not query:
                messagebox.showwarning("Ошибка", "Введите SQL запрос")
                return

            results = self.db_handler.execute_custom_query(query)

            # Очищаем таблицу результатов
            for item in self.query_result_tree.get_children():
                self.query_result_tree.delete(item)

            if results:
                # Настраиваем колонки
                columns = list(results[0].keys())
                self.query_result_tree["columns"] = columns

                # Устанавливаем заголовки
                for col in columns:
                    self.query_result_tree.heading(col, text=col)
                    self.query_result_tree.column(col, width=100)

                # Добавляем данные
                for row in results:
                    values = [row.get(col, '') for col in columns]
                    self.query_result_tree.insert("", tk.END, values=values)
            else:
                messagebox.showinfo("Результат", "Запрос выполнен успешно (нет данных для отображения)")

        except Exception as e:
            self.show_error("Ошибка выполнения запроса", str(e))

    def setup_database(self):
        """Настройка базы данных"""
        try:
            if setup_database():
                messagebox.showinfo("Успех", "База данных успешно настроена!")
                self.load_data_threaded()
            else:
                messagebox.showerror("Ошибка", "Не удалось настроить базу данных")
        except Exception as e:
            self.show_error("Ошибка настройки базы данных", str(e))

    def create_test_data(self):
        """Создание тестовых данных"""
        try:
            if create_test_data():
                messagebox.showinfo("Успех", "Тестовые данные созданы!")
                self.load_data_threaded()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать тестовые данные")
        except Exception as e:
            self.show_error("Ошибка создания тестовых данных", str(e))

    def test_connection(self):
        """Тест подключения к базе"""
        self.update_status_label()
        if self.db_handler.check_connection():
            messagebox.showinfo("Успех", "Подключение к PostgreSQL работает!")
        else:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных")

    def clear_customer_form(self):
        """Очистка формы клиента"""
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.address_text.delete(1.0, tk.END)

    def clear_product_form(self):
        """Очистка формы товара"""
        self.product_name_entry.delete(0, tk.END)
        self.product_sku_entry.delete(0, tk.END)
        self.product_category_combo.current(4)
        self.product_price_spinbox.delete(0, tk.END)
        self.product_price_spinbox.insert(0, "0")
        self.product_quantity_spinbox.delete(0, tk.END)
        self.product_quantity_spinbox.insert(0, "0")
        self.product_description_text.delete(1.0, tk.END)

    def show_error(self, title, message):
        """Показать окно ошибки"""
        messagebox.showerror(title, message)