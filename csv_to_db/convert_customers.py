import csv
import logging
from database import SessionLocal, Base, engine
from models import Customer

logging.basicConfig(
    filename='logs/problematic_rows.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def convert_customers():
    db = SessionLocal()
    successful = 0
    failed = 0

    try:
        with open("data/customers.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row_num, row in enumerate(reader, start=2):
                try:
                    # 1. СНАЧАЛА проверка
                    customer_existing = db.query(Customer).filter(
                        Customer.customer_id == int(row["customer_id"])
                    ).first()
                    
                    if customer_existing:
                        continue  # Пропустить
                    
                    # 2. ПОТОМ добавление
                    customer = Customer(
                        customer_id=int(row["customer_id"]),
                        name=row["name"],
                        email=row["email"],
                        phone=row["phone"]
                    )
                    db.add(customer)
                    successful += 1
                    
                except Exception as e:
                    logging.error(f"Строка {row_num}: {row} | Ошибка: {str(e)}")
                    failed += 1

        db.commit()
        print(f"Customers: успешно {successful}, ошибок {failed}")

    except Exception as e:
        db.rollback()
        logging.error(f"Критическая ошибка: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    convert_customers()
