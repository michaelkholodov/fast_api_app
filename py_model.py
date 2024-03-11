from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(UserCreate):
    id: int

class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(PostCreate):
    id: int

class ProductCreate(BaseModel):
    name: str
    price: float

class OrderCreate(BaseModel):
    product_id: int
    quantity: int