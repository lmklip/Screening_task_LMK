import models
import schemas
import logging

from database import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/products", tags=["Products"])
logging.basicConfig(level=logging.INFO, filename='logs/app.log', format='%(asctime)s - %(message)s')

@router.get("/", response_model=list[schemas.ProductResponse])
def get_products(
    page: int = 1,
    per_page: int = 20,
    category: str | None = None,
    price_min: float | None = None, 
    price_max: float | None = None,
    db: Session = Depends(get_db)
):
    logging.info(f"GET /products - /, page: {page}, category: {category}, price_min: {price_min}, price_max: {price_max}")
    query = db.query(models.Product) # выбираем всю таблицу
    
    # фильтруем
    if category:
        query = query.filter(models.Product.category == category)
    if price_min:
        query = query.filter(models.Product.price >= price_min)
    if price_max:
        query = query.filter(models.Product.price <= price_max)
        
    offset = (page - 1) * per_page # пропускаем товары с предыдущих страниц
    # Например: page=2, per_page=20 → offset = (2-1)*20 = 20 → пропускаем первые 20 товаров
    
    products = query.offset(offset).limit(per_page).all()
    # "пропусти N товаров, возьми следующие M товаров"
    
    return products