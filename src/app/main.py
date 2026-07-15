from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import os
import sqlite3
from contextlib import asynccontextmanager
from src.app.database import get_db_connection, init_db

# Get database path from environment variable
DB_PATH = os.getenv("DATABASE_PATH", "inventory.db")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code: Initialize database
    init_db(DB_PATH)
    yield
    # Teardown code (if any needed in future)

app = FastAPI(
    title="Product Inventory & Order API",
    description="A lightweight API for inventory and order management, designed for API & Database testing.",
    version="1.0.0",
    lifespan=lifespan
)

# --- Pydantic Schemas ---
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Wireless Mouse"])
    sku: str = Field(..., min_length=3, max_length=50, examples=["TECH-MOU-001"])
    price: float = Field(..., gt=0.0, examples=[29.99])
    stock: int = Field(..., ge=0, examples=[150])
    category: str = Field(..., min_length=1, max_length=50, examples=["Electronics"])

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    sku: Optional[str] = Field(None, min_length=3, max_length=50)
    price: Optional[float] = Field(None, gt=0.0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, min_length=1, max_length=50)

class ProductResponse(ProductBase):
    id: int

class OrderCreate(BaseModel):
    product_id: int = Field(..., examples=[1])
    quantity: int = Field(..., gt=0, examples=[2])
    customer_email: EmailStr = Field(..., examples=["buyer@example.com"])

class OrderResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    total_price: float
    customer_email: str
    status: str

# --- Endpoints ---

@app.post("/api/v1/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):
    conn = get_db_connection(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO products (name, sku, price, stock, category) VALUES (?, ?, ?, ?, ?)",
            (product.name, product.sku.upper(), product.price, product.stock, product.category)
        )
        conn.commit()
        product_id = cursor.lastrowid
        return {**product.model_dump(), "id": product_id, "sku": product.sku.upper()}
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU '{product.sku.upper()}' already exists."
        )
    finally:
        conn.close()

@app.get("/api/v1/products", response_model=List[ProductResponse])
def get_products(
    category: Optional[str] = None,
    min_price: Optional[float] = Query(None, gt=0.0),
    max_price: Optional[float] = Query(None, gt=0.0)
):
    conn = get_db_connection(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    if min_price is not None:
        query += " AND price >= ?"
        params.append(min_price)
    if max_price is not None:
        query += " AND price <= ?"
        params.append(max_price)
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@app.get("/api/v1/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    conn = get_db_connection(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )
    return dict(row)

@app.put("/api/v1/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate):
    conn = get_db_connection(DB_PATH)
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    existing_row = cursor.fetchone()
    if not existing_row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )
        
    update_data = product.model_dump(exclude_unset=True)
    if not update_data:
        conn.close()
        return dict(existing_row)
        
    fields = []
    params = []
    for k, v in update_data.items():
        fields.append(f"{k} = ?")
        params.append(v.upper() if k == "sku" else v)
        
    params.append(product_id)
    query = f"UPDATE products SET {', '.join(fields)} WHERE id = ?"
    
    try:
        cursor.execute(query, params)
        conn.commit()
        
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        updated_row = cursor.fetchone()
        return dict(updated_row)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product SKU update failed due to duplicate SKU."
        )
    finally:
        conn.close()

@app.delete("/api/v1/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    conn = get_db_connection(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )
        
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

@app.post("/api/v1/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate):
    conn = get_db_connection(DB_PATH)
    cursor = conn.cursor()
    
    # Get product
    cursor.execute("SELECT * FROM products WHERE id = ?", (order.product_id,))
    product = cursor.fetchone()
    if not product:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {order.product_id} not found."
        )
        
    # Check stock
    if product["stock"] < order.quantity:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {product['stock']}, Requested: {order.quantity}"
        )
        
    total_price = order.quantity * product["price"]
    
    try:
        # Start transaction
        cursor.execute("BEGIN;")
        # Decrement stock
        cursor.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (order.quantity, order.product_id)
        )
        # Create order
        cursor.execute(
            "INSERT INTO orders (product_id, quantity, total_price, customer_email, status) VALUES (?, ?, ?, ?, 'PAID')",
            (order.product_id, order.quantity, total_price, order.customer_email)
        )
        order_id = cursor.lastrowid
        conn.commit()
        
        return {
            "id": order_id,
            "product_id": order.product_id,
            "quantity": order.quantity,
            "total_price": total_price,
            "customer_email": order.customer_email,
            "status": "PAID"
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Order creation failed: {str(e)}"
        )
    finally:
        conn.close()

@app.get("/api/v1/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int):
    conn = get_db_connection(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found."
        )
    return dict(row)
