import csv
import logging
from database import SessionLocal, Base, engine
from models import Product

logging.basicConfig(
    filename='logs/problematic_rows.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def convert_products():
    db = SessionLocal()
    successful = 0
    failed = 0

    try:
        with open("data/products.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row_num, row in enumerate(reader, start=2):
                try:
                    # 1. СНАЧАЛА проверка
                    product_existing = db.query(Product).filter(
                        Product.product_id == int(row["product_id"])
                    ).first()
                    
                    if product_existing:
                        continue  # Пропустить
                    
                    # 2. ПОТОМ добавление
                    product = Product(
                        product_id=int(row["product_id"]),
                        name=row["name"],
                        category=row["category"],  # ← Исправлено
                        price=float(row["price"]),
                        stock=int(row["stock"])
                    )
                    db.add(product)
                    successful += 1
                    
                except Exception as e:
                    logging.error(f"Строка {row_num}: {row} | Ошибка: {str(e)}")
                    failed += 1

        db.commit()
        print(f"Products: успешно {successful}, ошибок {failed}")

    except Exception as e:
        db.rollback()
        logging.error(f"Критическая ошибка: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    convert_products()
