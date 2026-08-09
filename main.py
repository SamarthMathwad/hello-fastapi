from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel

app = FastAPI()


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    age: int


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int


@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    return {
        "id": 1,
        "name": user.name,
        "email": user.email,
        "age": user.age
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


@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {
        "message": "User Profile",
        "user_id": user_id
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