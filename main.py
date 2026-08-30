from fastapi import FastAPI, status, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel, Field, field_validator

app = FastAPI()


class UserCreate(BaseModel):
    name: str = Field(min_length=3)
    username: str = Field(min_length=3)
    email: str
    password: str = Field(min_length=8)
    age: int = Field(gt=0)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        if " " in value:
            raise ValueError("Username cannot contain spaces")
        return value


class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    email: str
    age: int


class ProductCreate(BaseModel):
    name: str = Field(min_length=3)
    description: Optional[str] = None
    in_stock: bool = True
    price: int = Field(gt=0)
    quantity: int = Field(ge=0)


@app.post("/products")
def create_product(product: ProductCreate):
    return {
        "name": product.name,
        "description": product.description,
        "in_stock": product.in_stock,
        "price": product.price,
        "quantity": product.quantity
    }


@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    return {
        "id": 1,
        "name": user.name,
        "username": user.username,
        "email": user.email,
        "age": user.age
    }


@app.post("/products/{product_id}/buy")
def buy_product(product_id: int, quantity: int = 1):
    available_stock = 5

    if quantity > available_stock:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock available."
        )

    return {
        "message": "Purchase successful",
        "product_id": product_id,
        "quantity": quantity
    }


@app.get("/")
def home():
    return {"message": "Hello World"}


@app.get("/about")
def about():
    return {
        "name": "Samarth Mathwad",
        "learning": "FastAPI"
    }



@app.get("/products")
def get_products(
    category: Optional[str] = None,
    limit: Optional[int] = 10
):
    return {
        "category": category,
        "limit": limit
    }


def get_user_details():
    return {
        "id": 1,
        "name": "Samarth",
        "age": 20
    }


@app.get("/profile")
def profile(user_details=Depends(get_user_details)):
    return {
        "message": "User Profile",
        "details": user_details
    }


def require_adult(user_details=Depends(get_user_details)):
    if user_details["age"] < 18:
        raise HTTPException(
            status_code=403,
            detail="You must be an adult to access this resource"
        )

    return user_details


@app.get("/adult-profile")
def adult_profile(user_details=Depends(require_adult)):
    return {
        "message": "Adult Profile",
        "details": user_details
    }