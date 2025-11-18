from pydantic import BaseModel, Field

class ProductResponse(BaseModel):
    product_id: int
    name: str
    category: str
    price: float
    stock: int
    
    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    product_id: int
    qty: int


class OrderItemResponse(BaseModel):
    product_id: int
    qty: int
    unit_price: float
    subtotal: float
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    customer_id: int
    items: list[OrderItemCreate]


class OrderResponse(BaseModel):
    order_id: int
    customer_id: int
    order_date: str
    total_amount: float
    items: list[OrderItemResponse]
    
    class Config:
        from_attributes = True
