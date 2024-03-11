from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
import requests

from py_model import UserResponse, UserCreate, PostResponse, PostCreate, ProductCreate
from alchemy_models import User, Post, Product, get_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float

# CRUD operations for Product model
@app.get("/products/", response_model=list[ProductResponse])
def list_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@app.get("/products/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/products/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}

# Background task to fetch data from the test API for cocktails and save to database
def fetch_data_and_save_to_db():
    response = requests.get("https://www.thecocktaildb.com/api/json/v1/1/search.php?s=margarita")
    data = response.json()
    db = next(get_db())
    try:
        for drink in data.get('drinks', []):
            db_drink = Product(name=drink['strDrink'], price=0)  # Assuming price is always 0 for simplicity
            db.add(db_drink)
        db.commit()
    finally:
        db.close()

@app.get("/task/")
def back_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(fetch_data_and_save_to_db)
    return {"task": "Start"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)