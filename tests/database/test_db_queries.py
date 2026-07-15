import sqlite3
import pytest

pytestmark = [pytest.mark.database, pytest.mark.regression]

def test_database_schema_tables(db_client):
    """Verify that products and orders tables exist with the correct columns."""
    # Query SQLite system catalog table sqlite_master
    tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = [row["name"] for row in db_client.execute_query(tables_query)]
    
    assert "products" in tables
    assert "orders" in tables

    # Verify column structures of products table
    columns_query = "PRAGMA table_info(products);"
    columns = db_client.execute_query(columns_query)
    column_names = [col["name"] for col in columns]
    expected_product_cols = ["id", "name", "sku", "price", "stock", "category", "created_at"]
    for col in expected_product_cols:
        assert col in column_names

def test_product_sku_unique_constraint(db_client, clean_db):
    """Verify that SQLite unique constraint on SKU is enforced at DB level."""
    # Insert a product directly in the DB
    query = "INSERT INTO products (name, sku, price, stock, category) VALUES (?, ?, ?, ?, ?);"
    db_client.execute_write(query, ("Keyboard", "KEY-MCH-87", 90.00, 10, "Peripherals"))
    
    # Try inserting duplicate SKU and expect IntegrityError
    with pytest.raises(sqlite3.IntegrityError) as exc_info:
        db_client.execute_write(query, ("Keyboard Duplicate", "KEY-MCH-87", 95.00, 5, "Peripherals"))
    
    assert "UNIQUE constraint failed" in str(exc_info.value)

def test_order_foreign_key_constraint(db_client, clean_db):
    """Verify that SQLite foreign key constraint is enforced on orders.product_id."""
    # Try placing an order for product_id 99999 (which does not exist)
    query = "INSERT INTO orders (product_id, quantity, total_price, customer_email, status) VALUES (?, ?, ?, ?, ?);"
    
    with pytest.raises(sqlite3.IntegrityError) as exc_info:
        db_client.execute_write(query, (99999, 1, 100.0, "test@test.org", "PAID"))
        
    assert "FOREIGN KEY constraint failed" in str(exc_info.value)

def test_product_default_created_at(db_client, clean_db):
    """Verify that SQLite automatically sets created_at default value."""
    # Insert product without created_at
    query = "INSERT INTO products (name, sku, price, stock, category) VALUES (?, ?, ?, ?, ?);"
    db_client.execute_write(query, ("Mouse", "MOU-01", 10.00, 5, "Peripherals"))
    
    # Fetch record and check created_at is not null
    record = db_client.execute_fetchone("SELECT created_at FROM products WHERE sku='MOU-01';")
    assert record is not None
    assert record["created_at"] is not None
    assert len(record["created_at"]) > 10

def test_cascade_delete(db_client, clean_db):
    """Verify that deleting a product deletes its orders due to ON DELETE CASCADE."""
    # Insert a product
    prod_query = "INSERT INTO products (name, sku, price, stock, category) VALUES (?, ?, ?, ?, ?);"
    db_client.execute_write(prod_query, ("Item X", "SKU-X", 10.0, 50, "Cat X"))
    product_id = db_client.execute_scalar("SELECT id FROM products WHERE sku='SKU-X';")
    
    # Insert an order for it
    order_query = "INSERT INTO orders (product_id, quantity, total_price, customer_email) VALUES (?, ?, ?, ?);"
    db_client.execute_write(order_query, (product_id, 2, 20.0, "buyer@domain.com"))
    
    # Verify order is there
    order_count = db_client.execute_scalar("SELECT COUNT(*) FROM orders WHERE product_id=?;", (product_id,))
    assert order_count == 1
    
    # Delete product
    db_client.execute_write("DELETE FROM products WHERE id=?;", (product_id,))
    
    # Verify order is automatically deleted by foreign key cascade
    post_order_count = db_client.execute_scalar("SELECT COUNT(*) FROM orders WHERE product_id=?;", (product_id,))
    assert post_order_count == 0
