from fastapi import FastAPI, Depends, HTTPException, status, Query
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
    def validate_username(cls, value: str):
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
    category: str = Field(min_length=2)
    in_stock: bool = True
    price: int = Field(gt=0)
    quantity: int = Field(ge=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: str
    in_stock: bool
    price: int
    quantity: int


class OrderResponse(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    total_price: int
    status: str


class InventoryEvent(BaseModel):
    event: str
    quantity: int
    remaining_stock: int


products = {}
orders = {}
inventory_history = {}

next_product_id = 1
next_order_id = 1


@app.get("/")
def home():
    return {
        "message": "FastAPI Backend is running"
    }


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(user: UserCreate):
    return {
        "id": 1,
        "name": user.name,
        "username": user.username,
        "email": user.email,
        "age": user.age
    }


@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(product: ProductCreate):
    global next_product_id

    product_id = next_product_id

    new_product = {
        "id": product_id,
        "name": product.name,
        "description": product.description,
        "category": product.category,
        "in_stock": product.quantity > 0,
        "price": product.price,
        "quantity": product.quantity
    }

    products[product_id] = new_product
    inventory_history[product_id] = [
        {
            "event": "Product created",
            "quantity": product.quantity,
            "remaining_stock": product.quantity
        }
    ]

    next_product_id += 1

    return new_product


@app.get("/products", response_model=list[ProductResponse])
def get_products(
    category: Optional[str] = None,
    min_price: Optional[int] = Query(default=None, ge=0),
    max_price: Optional[int] = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100)
):
    if min_price is not None and max_price is not None:
        if min_price > max_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="min_price cannot be greater than max_price"
            )

    filtered_products = list(products.values())

    if category:
        filtered_products = [
            product for product in filtered_products
            if product["category"].lower() == category.lower()
        ]

    if min_price is not None:
        filtered_products = [
            product for product in filtered_products
            if product["price"] >= min_price
        ]

    if max_price is not None:
        filtered_products = [
            product for product in filtered_products
            if product["price"] <= max_price
        ]

    start = (page - 1) * limit
    end = start + limit

    return filtered_products[start:end]


@app.get(
    "/products/{product_id}",
    response_model=ProductResponse
)
def get_product(product_id: int):
    if product_id not in products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return products[product_id]


@app.post(
    "/products/{product_id}/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_order(
    product_id: int,
    quantity: int = Query(default=1, gt=0)
):
    global next_order_id

    if product_id not in products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    product = products[product_id]

    if quantity > product["quantity"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough stock available"
        )

    product["quantity"] -= quantity
    product["in_stock"] = product["quantity"] > 0

    order_id = next_order_id

    order = {
        "order_id": order_id,
        "product_id": product_id,
        "quantity": quantity,
        "total_price": product["price"] * quantity,
        "status": "confirmed"
    }

    orders[order_id] = order

    inventory_history[product_id].append(
        {
            "event": "Order placed",
            "quantity": -quantity,
            "remaining_stock": product["quantity"]
        }
    )

    next_order_id += 1

    return order


@app.get(
    "/products/{product_id}/history",
    response_model=list[InventoryEvent]
)
def get_inventory_history(product_id: int):
    if product_id not in products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return inventory_history[product_id]


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int):
    if order_id not in orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return orders[order_id]


def get_user_details() -> dict:
    return {
        "id": 1,
        "name": "Samarth",
        "age": 20
    }


def require_adult(
    user_details: dict = Depends(get_user_details)
) -> dict:
    if user_details["age"] < 18:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be an adult to access this resource"
        )

    return user_details


@app.get("/profile")
def profile(
    user_details: dict = Depends(get_user_details)
):
    return {
        "message": "User Profile",
        "details": user_details
    }


@app.get("/adult-profile")
def adult_profile(
    user_details: dict = Depends(require_adult)
):
    return {
        "message": "Adult Profile",
        "details": user_details
    }
