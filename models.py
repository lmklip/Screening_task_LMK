from sqlalchemy import Column, Integer, String, Float, DateTime, Numeric, ForeignKey
from database import Base
from datetime import datetime
import json

class Product(Base):
    __tablename__ = "Products"
    
    product_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False) # поле обязательно к заполнению
    category = Column(String(100), nullable=True) 
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=True)

class Customer(Base):
    __tablename__ = "Customers"
    
    customer_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String, nullable=False)
    
class Order(Base):
    __tablename__ = "Orders"
    
    order_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('Customers.customer_id'))
    order_date = Column(String)
    total_amount = Column(Float)

class OrderItem(Base):
    __tablename__ = "OrderItems"
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # ← Добавь ID!
    order_id = Column(Integer, ForeignKey('Orders.order_id'))   # ← Это ОБЯЗАТЕЛЬНО
    product_id = Column(Integer, ForeignKey('Products.product_id'))
    qty = Column(Integer)
    unit_price = Column(Float)
    subtotal = Column(Float)
    