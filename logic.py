import sqlite3
from config import DATABASE

class DB_Manager:
    def __init__(self, database):
        self.database = database

    def create_database(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )''')

            conn.execute('''
            CREATE TABLE IF NOT EXISTS dishes (
                dish_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                category_id INTEGER,
                available BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            )''')

            conn.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT,
                email TEXT
            )''')

            conn.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT CHECK(status IN ('новый', 'в обработке', 'готовится', 'в пути', 'доставлен', 'отменен')) DEFAULT 'новый',
                total_amount REAL,
                delivery_address TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )''')

            conn.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                dish_id INTEGER,
                quantity INTEGER NOT NULL DEFAULT 1,
                price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (dish_id) REFERENCES dishes(dish_id)
            )''')

            conn.execute('''
            INSERT OR IGNORE INTO categories (category_id, name, description) VALUES 
                (1, 'Пицца', 'Итальянская пицца на тонком и толстом тесте'),
                (2, 'Суши', 'Традиционные японские роллы и суши'),
                (3, 'Бургеры', 'Американские бургеры с разными начинками'),
                (4, 'Салаты', 'Свежие и полезные салаты'),
                (5, 'Напитки', 'Холодные и горячие напитки')
            ''')

            conn.execute('''
            INSERT OR IGNORE INTO dishes (dish_id, name, description, price, category_id) VALUES 
                (1, 'Пицца Маргарита', 'Классическая пицца с томатным соусом, моцареллой и базиликом', 450, 1),
                (2, 'Пицца Пепперони', 'Пицца с острой колбаской пепперони и сыром', 550, 1),
                (3, 'Калифорния', 'Ролл с крабом, огурцом и авокадо', 320, 2),
                (4, 'Филадельфия', 'Ролл с лососем и сливочным сыром', 380, 2),
                (5, 'Чизбургер', 'Классический бургер с говяжьей котлетой и сыром', 280, 3),
                (6, 'Вегги бургер', 'Бургер с овощной котлетой', 250, 3),
                (7, 'Греческий салат', 'Салат с огурцами, помидорами, оливками и фетой', 220, 4),
                (8, 'Цезарь', 'Салат с курицей, сухариками и соусом цезарь', 240, 4),
                (9, 'Кола', 'Газированный напиток 0.5л', 100, 5),
                (10, 'Кофе латте', 'Кофе с молоком 250мл', 150, 5),

                -- Дополнительные блюда
                (11, 'Пицца Четыре сыра', 'Сырная пицца с моцареллой, дорблю, пармезаном и эмменталем', 590, 1),
                (12, 'Пицца Гавайская', 'Пицца с курицей, ананасами и сыром', 520, 1),
                (13, 'Пицца Барбекю', 'Пицца с говядиной, соусом BBQ и луком', 610, 1),

                (14, 'Ролл Спайси тунец', 'Острый ролл с тунцом и соусом чили', 400, 2),
                (15, 'Ролл Унаги', 'Ролл с копченым угрем и кунжутом', 460, 2),
                (16, 'Сет Ассорти', 'Набор из 20 штук: роллы, суши, маки', 980, 2),

                (17, 'Бекон бургер', 'Бургер с беконом, сыром и карамелизированным луком', 320, 3),
                (18, 'Двойной бургер', 'Бургер с двумя котлетами и двойным сыром', 390, 3),
                (19, 'Острый бургер', 'Бургер с халапеньо и острым соусом', 350, 3),

                (20, 'Салат с тунцом', 'Салат с консервированным тунцом и яйцом', 260, 4),
                (21, 'Овощной салат', 'Свежие овощи с зеленью и оливковым маслом', 200, 4),
                (22, 'Салат с креветками', 'Лёгкий салат с креветками и соусом', 320, 4),

                (23, 'Сок апельсиновый', '100% натуральный сок 0.3л', 120, 5),
                (24, 'Минеральная вода', 'Газированная минеральная вода 0.5л', 90, 5),
                (25, 'Чай зелёный', 'Горячий зелёный чай 300мл', 100, 5)
            ''')

            conn.commit()

    def add_user(self, customer_id, name, phone):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute(
                'INSERT OR IGNORE INTO customers (customer_id, name, phone) VALUES (?, ?, ?)',
                (customer_id, name, phone)
            )
            conn.commit()

    def get_user(self, customer_id):
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        cur.execute('SELECT * FROM customers WHERE customer_id = ?', (customer_id,))
        return cur.fetchone()

    def add_dish(self, name, price, category_id):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute(
                'INSERT INTO dishes (name, price, category_id) VALUES (?, ?, ?)',
                (name, price, category_id)
            )

    def get_dishes(self, category_id=None):
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        if category_id:
            cur.execute('SELECT * FROM dishes WHERE category_id = ?', (category_id,))
        else:
            cur.execute('SELECT * FROM dishes')
        return cur.fetchall()

    def get_categories(self):
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        cur.execute('SELECT category_id, name FROM categories')
        return cur.fetchall()

    def create_order(self, customer_id, dish_id):
        conn = sqlite3.connect(self.database)
        with conn:
            print(f"Создан заказ для пользователя {customer_id} с блюдами: {dish_id}")
            return True
