import sys
import sqlite3
import datetime

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QTableWidgetItem


class OrderForm(QWidget):
    def __init__(self):
        super().__init__()

        # Загружаем UI
        uic.loadUi("Main.ui", self)
        self.setWindowTitle("Создание заказа")

        self.conn = sqlite3.connect("import_data.db")
        self.cursor = self.conn.cursor()

        self.current_items = []  # товары в текущем заказе

        self.addItemButton.clicked.connect(self.add_item)
        self.createOrderButton.clicked.connect(self.save_order)

        self.load_customers()
        self.load_products()

    # ==========================================================
    # ЗАГРУЗКА КЛИЕНТОВ
    # ==========================================================
    def load_customers(self):
        self.cursor.execute("SELECT customer_id, email FROM customers")
        rows = self.cursor.fetchall()

        self.customerSelect.clear()

        for cid, email in rows:
            self.customerSelect.addItem(f"{email}", f"{cid}")

    # ==========================================================
    # ЗАГРУЗКА ТОВАРОВ
    # ==========================================================
    def load_products(self):
        self.cursor.execute("SELECT product_id, name, price, stock FROM products")
        rows = self.cursor.fetchall()

        self.product_data = {}

        self.productSelect.clear()
        for pid, name, price, stock in rows:
            self.productSelect.addItem(f"{name} ({stock} шт.)", pid)
            self.product_data[pid] = {"name": name, "price": price, "stock": stock}

    # ==========================================================
    # ДОБАВЛЕНИЕ ТОВАРА В ТАБЛИЦУ
    # ==========================================================
    def add_item(self):
        pid = self.productSelect.currentData()
        qty = self.qtySpin.value()

        product = self.product_data[pid]

        if qty > product["stock"]:
            QMessageBox.warning(self, "Ошибка", "Недостаточно товара на складе!")
            return

        subtotal = qty * product["price"]

        self.current_items.append({
            "id": pid,
            "name": product["name"],
            "qty": qty,
            "price": product["price"],
            "subtotal": subtotal
        })

        self.update_items_table()

    # ==========================================================
    # ОБНОВЛЕНИЕ ТАБЛИЦЫ ТОВАРОВ
    # ==========================================================
    def update_items_table(self):
        self.itemsTable.setRowCount(len(self.current_items))

        total = 0

        for row, item in enumerate(self.current_items):
            self.itemsTable.setItem(row, 0, QTableWidgetItem(item["name"]))
            self.itemsTable.setItem(row, 1, QTableWidgetItem(str(item["qty"])))
            self.itemsTable.setItem(row, 2, QTableWidgetItem(str(item["price"])))
            self.itemsTable.setItem(row, 3, QTableWidgetItem(str(item["subtotal"])))

            total += item["subtotal"]

        self.totalAmountLabel.setText(str(round(total, 2)))

    # ==========================================================
    # СОХРАНЕНИЕ ЗАКАЗА В БАЗУ
    # ==========================================================
    def save_order(self):
        if not self.current_items:
            QMessageBox.warning(self, "Ошибка", "Добавьте товары в заказ!")
            return

        customer_id = self.customerSelect.currentData()
        total = float(self.totalAmountLabel.text())

        order_date = datetime.datetime.now().strftime("%Y-%m-%d")

        self.cursor.execute(
            "INSERT INTO orders (customer_id, total_amount, order_date) VALUES (?, ?, ?)",
            (customer_id, total, order_date)
        )

        order_id = self.cursor.lastrowid

        # Записываем позицию и уменьшаем склад
        for item in self.current_items:
            self.cursor.execute(
                "INSERT INTO order_items (order_id, product_id, qty, unit_price, subtotal) "
                "VALUES (?, ?, ?, ?, ?)",
                (order_id, item["id"], item["qty"], item["price"], item["subtotal"])
            )

            self.cursor.execute(
                "UPDATE products SET stock = stock - ? WHERE product_id = ?",
                (item["qty"], item["id"])
            )

        self.conn.commit()

        QMessageBox.information(self, "Готово", f"Заказ #{order_id} успешно создан!")

        self.current_items = []
        self.update_items_table()
        self.load_products()


# ==========================================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# ==========================================================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OrderForm()
    window.show()
    sys.exit(app.exec_())
