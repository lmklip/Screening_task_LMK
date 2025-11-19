import uvicorn
import logging

from routers import orders, products
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO, filename='logs/app.log', format='%(asctime)s - %(message)s')
app = FastAPI(
    title="OrderManager",
    version="0.0.1",
    description="OrderManager — мини-система заказов"
)

app.include_router(orders.router)
app.include_router(products.router)

app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"],
    allow_origins=["*"],
    allow_methods=["*"], 
    allow_credentials=True
)

@app.get("/")
def wellcome():
    logging.info("GET /")
    return{
        "message": "Добро пожаловать в нашу OrderManager",
        "detail": "Документация: http://127.0.0.1:8000/docs"
    }
    
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)