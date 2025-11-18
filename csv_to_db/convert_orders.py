import csv
import logging
import json
from models import Order, OrderItem
from database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

logging.basicConfig(
    level=logging.ERROR,
    filename="logs/problematic_rows.log",
    encoding="utf-8",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def convert_orders():
    db = SessionLocal()
    successful = 0
    failed = 0
    
    try:
        with open("data/sample_orders.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # 1. СНАЧАЛА проверка
                    order_existing = db.query(Order).filter_by(
                        order_id=int(row['order_id'])
                    ).first()
                    
                    if order_existing:
                        continue  # Пропустить
                    
                    # 2. ПОТОМ создание
                    order = Order(
                        order_id=int(row['order_id']),
                        customer_id=int(row['customer_id']),
                        order_date=row['order_date'],
                        total_amount=float(row['total_amount'])
                    )
                    db.add(order)
                    successful += 1
                    
                except Exception as e:
                    logging.error(f"Строка {row_num}: {row} | Ошибка: {str(e)}")
                    failed += 1
        
        db.commit()
        print(f"Orders: успешно {successful}, ошибок {failed}")
        
    except Exception as e:
        db.rollback()
        logging.error(f"Критическая ошибка: {str(e)}")
    finally:
        db.close()


def fill_orderItems():
    db = SessionLocal()
    successful = 0
    failed = 0
    
    try:
        with open("data/sample_orders.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Проверка на дубликаты
                    existing_items = db.query(OrderItem).filter_by(
                        order_id=int(row['order_id'])
                    ).first()
                    
                    if existing_items:
                        continue
                    
                    items = json.loads(row['items'])
                    
                    for item in items:
                        order_item = OrderItem(
                            order_id=int(row['order_id']),
                            product_id=int(item['product_id']),
                            qty=int(item['qty']),
                            unit_price=float(item['unit_price']),
                            subtotal=float(item['subtotal'])
                        )
                        db.add(order_item)
                    
                    successful += 1
                    
                except Exception as e:
                    logging.error(f"Строка {row_num} | Ошибка: {str(e)}")
                    failed += 1
        
        db.commit()
        print(f"OrderItems: успешно {successful}, ошибок {failed}")
        
    except Exception as e:
        db.rollback()
        logging.error(f"Критическая ошибка: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    convert_orders()
    fill_orderItems()
