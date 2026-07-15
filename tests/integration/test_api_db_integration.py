import pytest

pytestmark = [pytest.mark.integration, pytest.mark.regression]

def test_api_post_creates_database_record(api_client, db_client, clean_db):
    """Verify that a product created via the API is saved correctly in the SQLite database."""
    product_payload = {
        "name": "Mechanical Keyboard",
        "sku": "KEY-MCH-87",
        "price": 89.99,
        "stock": 45,
        "category": "Peripherals"
    }
    
    # 1. Create product via API
    api_response = api_client.post("api/v1/products", json_data=product_payload)
    assert api_response.status_code == 201
    api_data = api_response.json()
    product_id = api_data["id"]
    
    # 2. Query the SQLite database directly
    db_record = db_client.execute_fetchone("SELECT * FROM products WHERE id = ?;", (product_id,))
    
    # 3. Assert exact data consistency between API response and Database record
    assert db_record is not None
    assert db_record["id"] == product_id
    assert db_record["name"] == product_payload["name"]
    assert db_record["sku"] == product_payload["sku"].upper()
    assert db_record["price"] == product_payload["price"]
    assert db_record["stock"] == product_payload["stock"]
    assert db_record["category"] == product_payload["category"]

def test_api_put_updates_database_record(api_client, db_client, clean_db):
    """Verify that updating a product via the API updates the SQLite database record."""
    # 1. Create initial product via API
    created = api_client.post("api/v1/products", json_data={
        "name": "Old Monitor", "sku": "MON-OLD-01", "price": 150.00, "stock": 10, "category": "Displays"
    }).json()
    product_id = created["id"]
    
    # 2. Update via API
    update_payload = {"price": 139.99, "stock": 8}
    api_response = api_client.put(f"api/v1/products/{product_id}", json_data=update_payload)
    assert api_response.status_code == 200
    
    # 3. Query the database and verify updates
    db_record = db_client.execute_fetchone("SELECT price, stock FROM products WHERE id = ?;", (product_id,))
    assert db_record is not None
    assert db_record["price"] == 139.99
    assert db_record["stock"] == 8

def test_api_delete_removes_database_record(api_client, db_client, clean_db):
    """Verify that deleting a product via the API deletes the database record."""
    # 1. Create initial product via API
    created = api_client.post("api/v1/products", json_data={
        "name": "Disposable Item", "sku": "DISP-01", "price": 1.00, "stock": 5, "category": "Other"
    }).json()
    product_id = created["id"]
    
    # 2. Delete via API
    del_response = api_client.delete(f"api/v1/products/{product_id}")
    assert del_response.status_code == 204
    
    # 3. Verify record does not exist in DB
    db_record = db_client.execute_fetchone("SELECT * FROM products WHERE id = ?;", (product_id,))
    assert db_record is None

def test_api_order_flow_db_side_effects(api_client, db_client, clean_db):
    """Verify that ordering via API inserts order table record and decrements stock in products table."""
    # 1. Create product via API with 10 stock
    product = api_client.post("api/v1/products", json_data={
        "name": "USB Cable", "sku": "USB-CBL-05", "price": 5.00, "stock": 10, "category": "Cables"
    }).json()
    product_id = product["id"]
    
    # 2. Place order via API for 3 units
    order_payload = {
        "product_id": product_id,
        "quantity": 3,
        "customer_email": "purchaser@domain.com"
    }
    order_response = api_client.post("api/v1/orders", json_data=order_payload)
    assert order_response.status_code == 201
    order_id = order_response.json()["id"]
    
    # 3. DB Side-Effect 1: Verify order record is present in DB and totals match
    db_order = db_client.execute_fetchone("SELECT * FROM orders WHERE id = ?;", (order_id,))
    assert db_order is not None
    assert db_order["product_id"] == product_id
    assert db_order["quantity"] == 3
    assert db_order["total_price"] == 15.00  # 3 * 5.00
    assert db_order["customer_email"] == "purchaser@domain.com"
    assert db_order["status"] == "PAID"
    
    # 4. DB Side-Effect 2: Verify stock was decremented correctly from 10 to 7 in products table
    db_product = db_client.execute_fetchone("SELECT stock FROM products WHERE id = ?;", (product_id,))
    assert db_product is not None
    assert db_product["stock"] == 7
