import pytest
from src.utils.helpers import validate_json_schema

pytestmark = [pytest.mark.api, pytest.mark.regression]

@pytest.mark.smoke
def test_create_product_success(api_client, clean_db):
    """Verify that a product can be successfully created with valid data."""
    payload = {
        "name": "Mechanical Keyboard",
        "sku": "KEY-MCH-87",
        "price": 89.99,
        "stock": 45,
        "category": "Peripherals"
    }
    
    response = api_client.post("api/v1/products", json_data=payload)
    
    # Assert HTTP status code
    assert response.status_code == 201
    
    # Validate JSON Schema
    data = response.json()
    assert validate_json_schema(data, "product_schema.json")
    
    # Assert Response Body values
    assert data["id"] > 0
    assert data["name"] == payload["name"]
    assert data["sku"] == payload["sku"].upper()
    assert data["price"] == payload["price"]
    assert data["stock"] == payload["stock"]
    assert data["category"] == payload["category"]
    
    # Assert Response Headers
    assert "application/json" in response.headers.get("Content-Type", "")

def test_get_product_by_id_success(api_client, clean_db):
    """Verify that a product can be fetched by its database ID."""
    # Setup: Create a product
    payload = {"name": "Gaming Mouse", "sku": "MOU-GME-12", "price": 49.99, "stock": 100, "category": "Peripherals"}
    created = api_client.post("api/v1/products", json_data=payload).json()
    product_id = created["id"]
    
    # Action: Fetch the product
    response = api_client.get(f"api/v1/products/{product_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert validate_json_schema(data, "product_schema.json")
    assert data["id"] == product_id
    assert data["name"] == payload["name"]

def test_get_all_products(api_client, clean_db):
    """Verify that the API returns a list of all products."""
    # Setup: Create two products
    p1 = {"name": "Item A", "sku": "SKU-A", "price": 10.0, "stock": 5, "category": "Cat A"}
    p2 = {"name": "Item B", "sku": "SKU-B", "price": 20.0, "stock": 10, "category": "Cat B"}
    api_client.post("api/v1/products", json_data=p1)
    api_client.post("api/v1/products", json_data=p2)
    
    # Action: Get list
    response = api_client.get("api/v1/products")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    for item in data:
        assert validate_json_schema(item, "product_schema.json")

def test_get_products_filtered_by_category(api_client, clean_db):
    """Verify listing products filtered by category query parameter."""
    p1 = {"name": "Laptop", "sku": "LAP-01", "price": 999.0, "stock": 10, "category": "Computers"}
    p2 = {"name": "Monitor", "sku": "MON-01", "price": 299.0, "stock": 15, "category": "Peripherals"}
    api_client.post("api/v1/products", json_data=p1)
    api_client.post("api/v1/products", json_data=p2)
    
    response = api_client.get("api/v1/products", params={"category": "Computers"})
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "Computers"
    assert data[0]["sku"] == "LAP-01"

def test_get_products_filtered_by_price_range(api_client, clean_db):
    """Verify listing products filtered by price boundaries."""
    p1 = {"name": "Pen", "sku": "PEN-01", "price": 1.50, "stock": 100, "category": "Stationery"}
    p2 = {"name": "Notebook", "sku": "NOTE-01", "price": 5.00, "stock": 50, "category": "Stationery"}
    p3 = {"name": "Desk Lamp", "sku": "LAMP-01", "price": 25.00, "stock": 20, "category": "Furniture"}
    api_client.post("api/v1/products", json_data=p1)
    api_client.post("api/v1/products", json_data=p2)
    api_client.post("api/v1/products", json_data=p3)
    
    # Filter: price between 3.00 and 10.00
    response = api_client.get("api/v1/products", params={"min_price": 3.00, "max_price": 10.00})
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["sku"] == "NOTE-01"

def test_update_product_success(api_client, clean_db):
    """Verify updating a product's stock and price via PUT request."""
    # Setup
    created = api_client.post("api/v1/products", json_data={
        "name": "Smart Watch", "sku": "WAT-SMT-01", "price": 199.99, "stock": 50, "category": "Wearables"
    }).json()
    product_id = created["id"]
    
    update_payload = {"price": 179.99, "stock": 42}
    
    # Action
    response = api_client.put(f"api/v1/products/{product_id}", json_data=update_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert validate_json_schema(data, "product_schema.json")
    assert data["price"] == 179.99
    assert data["stock"] == 42
    assert data["name"] == "Smart Watch" # Unchanged field remains identical

def test_delete_product_success(api_client, clean_db):
    """Verify deleting a product by ID."""
    created = api_client.post("api/v1/products", json_data={
        "name": "Trash Item", "sku": "TRASH-01", "price": 0.99, "stock": 1, "category": "Other"
    }).json()
    product_id = created["id"]
    
    # Delete
    del_response = api_client.delete(f"api/v1/products/{product_id}")
    assert del_response.status_code == 204
    
    # Verify no longer exists
    get_response = api_client.get(f"api/v1/products/{product_id}")
    assert get_response.status_code == 404

def test_create_product_duplicate_sku_fails(api_client, clean_db):
    """Verify duplicates on Unique SKU constraint return HTTP 400."""
    p1 = {"name": "Product 1", "sku": "DUP-SKU-99", "price": 10.00, "stock": 10, "category": "Test"}
    p2 = {"name": "Product 2", "sku": "dup-sku-99", "price": 20.00, "stock": 5, "category": "Test"} # lowercase gets capitalized
    
    r1 = api_client.post("api/v1/products", json_data=p1)
    assert r1.status_code == 201
    
    r2 = api_client.post("api/v1/products", json_data=p2)
    assert r2.status_code == 400
    assert "already exists" in r2.json()["detail"]

@pytest.mark.parametrize("invalid_field,value,expected_status", [
    ("price", -5.00, 422),
    ("price", 0.00, 422),
    ("stock", -1, 422),
    ("name", "", 422),
    ("sku", "XY", 422) # min length is 3
])
def test_create_product_invalid_fields_fail(api_client, clean_db, invalid_field, value, expected_status):
    """Verify boundary checks and schema validations fail with HTTP 422."""
    payload = {
        "name": "Standard Laptop",
        "sku": "LAP-STD-99",
        "price": 499.99,
        "stock": 10,
        "category": "Computers"
    }
    payload[invalid_field] = value
    
    response = api_client.post("api/v1/products", json_data=payload)
    assert response.status_code == expected_status

def test_create_product_missing_required_fields_fails(api_client, clean_db):
    """Verify that creating a product missing required fields returns HTTP 422."""
    payload = {
        "name": "Incomplete Product"
        # missing sku, price, stock, category
    }
    response = api_client.post("api/v1/products", json_data=payload)
    assert response.status_code == 422

def test_get_non_existent_product_fails(api_client, clean_db):
    """Verify fetching a non-existent product returns HTTP 404."""
    response = api_client.get("api/v1/products/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_update_non_existent_product_fails(api_client, clean_db):
    """Verify updating a non-existent product returns HTTP 404."""
    response = api_client.put("api/v1/products/99999", json_data={"price": 10.00})
    assert response.status_code == 404

def test_delete_non_existent_product_fails(api_client, clean_db):
    """Verify deleting a non-existent product returns HTTP 404."""
    response = api_client.delete("api/v1/products/99999")
    assert response.status_code == 404

def test_api_response_time(api_client, clean_db):
    """Verify that response latency is within acceptable limits (< 200ms)."""
    # Create product
    p = {"name": "Cable", "sku": "CBL-01", "price": 9.99, "stock": 50, "category": "Cables"}
    api_client.post("api/v1/products", json_data=p)
    
    # Get call
    response = api_client.get("api/v1/products")
    assert response.status_code == 200
    
    # Check custom elapsed property added by client
    assert response.elapsed_ms < 200.0, f"Latency too high: {response.elapsed_ms:.2f}ms"
