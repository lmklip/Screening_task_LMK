import models
import schemas
import logging

from database import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

logging.basicConfig(level=logging.INFO, filename='logs/app.log', format='%(asctime)s - %(message)s')

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    logging.info(f"GET /orders - /{order_id}")
    order = db.query(models.Order).filter(
        models.Order.order_id == order_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    
    order_items = db.query(models.OrderItem).filter(
       models.OrderItem.order_id == order_id 
    ).all()
    
    return {
        "order_id": order.order_id,
        "customer_id": order.customer_id,
        "order_date": order.order_date,
        "total_amount": order.total_amount,
        "items": [{"product_id": i.product_id, "qty": i.qty, "unit_price": i.unit_price, "subtotal": i.subtotal} for i in order_items]
    }

@router.post("/", response_model=schemas.OrderResponse)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    try:
        logging.info(f"POST /orders - customer_id: {order.customer_id}, items: {order.items}")
        
        customer = db.query(models.Customer).filter(
            models.Customer.customer_id == order.customer_id
        ).first()
        if not customer:
            logging.error(f"Customer {order.customer_id} не найден")
            raise HTTPException(status_code=400, detail=f"Клиент с ID {order.customer_id} не найден")
        
        total = 0
        items_data = []
        
        for item in order.items:
            product = db.query(models.Product).filter(
                models.Product.product_id == item.product_id
            ).first()
            
            if not product:
                logging.error(f"Product {item.product_id} не найден")
                raise HTTPException(status_code=400, detail=f"Продукт {item.product_id} не найден")
            
            if product.stock < item.qty:
                logging.error(f"Недостаточно stock для продукта {item.product_id}: есть {product.stock}, требуется {item.qty}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Недостаточно товара '{product.name}' на складе. Доступно: {product.stock}, запрошено: {item.qty}"
                )
            
            subtotal = product.price * item.qty
            total += subtotal
            
            items_data.append({
                "product": product,
                "qty": item.qty,
                "unit_price": product.price,
                "subtotal": subtotal
            })
        
        db_order = models.Order(
            customer_id=order.customer_id,
            order_date=datetime.now().strftime("%Y-%m-%d"),
            total_amount=total
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        order_items = []
        for item_data in items_data:
            db_item = models.OrderItem(
                order_id=db_order.order_id,
                product_id=item_data["product"].product_id,
                qty=item_data["qty"],
                unit_price=item_data["unit_price"],
                subtotal=item_data["subtotal"]
            )
            db.add(db_item)
            
            item_data["product"].stock -= item_data["qty"]
            
            order_items.append({
                "product_id": db_item.product_id,
                "qty": db_item.qty,
                "unit_price": db_item.unit_price,
                "subtotal": db_item.subtotal
            })
        
        db.commit()
        
        logging.info(f"Заказ {db_order.order_id} успешно создан, сумма: {total}")
        
        return {
            "order_id": db_order.order_id,
            "customer_id": db_order.customer_id,
            "order_date": db_order.order_date,
            "total_amount": db_order.total_amount,
            "items": order_items
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Ошибка при создании заказа: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")