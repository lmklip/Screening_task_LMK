from csv_to_db import convert_products, convert_customers, convert_orders

if __name__ == "__main__":
    print("Импорт products...")
    convert_products.convert_products()
    
    print("Импорт customers...")
    convert_customers.convert_customers()
    
    print("Импорт orders...")
    convert_orders.convert_orders()
