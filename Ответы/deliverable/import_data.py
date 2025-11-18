import csv
import json
import sqlite3
from datetime import datetime

DB_NAME = "import_data.db"
ERROR_LOG = "problematic_rows.log"


# ----------------------------------------------------
# Функция для записи ошибок в лог
# ----------------------------------------------------
def log_error(row, reason):
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"{reason} | data: {row}\n")

# ----------------------------------------------------
# Создание структуры таблиц БД
# ----------------------------------------------------
def create_tables(conn):
    cursor = conn.cursor()

    # Таблица клиентов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT
        )
    """)

    # Таблица товаров
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER
        )
    """)

    # Таблица заказов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            total_amount REAL,
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
        )
    """)

    # Таблица позиций заказа
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            qty INTEGER,
            unit_price REAL,
            subtotal REAL,
            FOREIGN KEY(order_id) REFERENCES orders(order_id),
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        )
    """)

    conn.commit()


# ----------------------------------------------------
# Импорт customers.csv
# ----------------------------------------------------
def import_customers(conn, filename="customers.csv"):
    cursor = conn.cursor()

    with open(filename, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                customer_id = int(row["customer_id"])
                name = row["name"].strip()
                email = row["email"].strip()

                cursor.execute("""
                    INSERT INTO customers (customer_id, name, email, phone)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(customer_id) DO UPDATE SET
                        name=excluded.name,
                        email=excluded.email,
                        phone=excluded.phone
                """, (customer_id, name, email, row["phone"]))

            except Exception as e:
                log_error(row, f"Ошибка при импорте customers: {e}")

    conn.commit()


# ----------------------------------------------------
# Импорт products.csv
# ----------------------------------------------------
def import_products(conn, filename="products.csv"):
    cursor = conn.cursor()

    with open(filename, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                product_id = int(row["product_id"])
                price = float(row["price"])
                stock = int(row["stock"])

                cursor.execute("""
                    INSERT INTO products (product_id, name, category, price, stock)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(product_id) DO UPDATE SET
                        name=excluded.name,
                        category=excluded.category,
                        price=excluded.price,
                        stock=excluded.stock
                """, (product_id, row["name"], row["category"], price, stock))

            except Exception as e:
                log_error(row, f"Ошибка при импорте products: {e}")

    conn.commit()


# ----------------------------------------------------
# Импорт sample_orders.csv
# ----------------------------------------------------
def import_orders(conn, filename="sample_orders.csv"):
    cursor = conn.cursor()

    with open(filename, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                order_id = int(row["order_id"])
                customer_id = int(row["customer_id"])
                order_date = row["order_date"]
                total_amount = float(row["total_amount"])

                cursor.execute("""
                    INSERT INTO orders (order_id, customer_id, order_date, total_amount)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(order_id) DO UPDATE SET
                        customer_id=excluded.customer_id,
                        order_date=excluded.order_date,
                        total_amount=excluded.total_amount
                """, (order_id, customer_id, order_date, total_amount))

                # Items в JSON
                items = json.loads(row["items"].replace("'", '"'))

                # Удаляем старые позиции заказа
                cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))

                for item in items:
                    cursor.execute("""
                        INSERT INTO order_items (order_id, product_id, qty, unit_price, subtotal)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        order_id,
                        item["product_id"],
                        item["qty"],
                        item["unit_price"],
                        item["subtotal"]
                    ))

            except Exception as e:
                log_error(row, f"Ошибка при импорте orders: {e}")

    conn.commit()


def main():
    print("Создаём или обновляем базу данных…")
    conn = sqlite3.connect(DB_NAME)

    create_tables(conn)

    print("Импортируем customers.csv")
    import_customers(conn)

    print("Импортируем products.csv")
    import_products(conn)

    print("Импортируем sample_orders.csv")
    import_orders(conn)

    conn.close()
    print("Готово! База данных сохранена под названием:", DB_NAME)


if __name__ == "__main__":
    main()
