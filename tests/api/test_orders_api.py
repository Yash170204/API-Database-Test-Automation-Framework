import pytest
from src.utils.helpers import validate_json_schema

pytestmark = [pytest.mark.api, pytest.mark.regression]

@pytest.fixture
def test_product(api_client):
    """Fixture to ensure a product exists for ordering."""
    payload = {"name": "SSD 1TB", "sku": "SSD-1TB-00", "price": 120.00, "stock": 10, "category": "Storage"}
    product = api_client.post("api/v1/products", json_data=payload).json()
    return product

@pytest.mark.smoke
def test_create_order_success(api_client, clean_db, test_product):
    """Verify that a customer can successfully order an item with enough stock."""
    payload = {
        "product_id": test_product["id"],
        "quantity": 2,
        "customer_email": "customer@example.com"
    }
    
    response = api_client.post("api/v1/orders", json_data=payload)
    
    assert response.status_code == 201
    data = response.json()
    
    # Schema validation
    assert validate_json_schema(data, "order_schema.json")
    
    # Value asserts
    assert data["id"] > 0
    assert data["product_id"] == test_product["id"]
    assert data["quantity"] == 2
    assert data["total_price"] == 2 * test_product["price"]
    assert data["customer_email"] == payload["customer_email"]
    assert data["status"] == "PAID"

def test_get_order_by_id_success(api_client, clean_db, test_product):
    """Verify retrieving an order's status and details by database ID."""
    order = api_client.post("api/v1/orders", json_data={
        "product_id": test_product["id"], "quantity": 1, "customer_email": "buyer@test.org"
    }).json()
    order_id = order["id"]
    
    response = api_client.get(f"api/v1/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert validate_json_schema(data, "order_schema.json")
    assert data["id"] == order_id
    assert data["total_price"] == test_product["price"]

def test_create_order_non_existent_product_fails(api_client, clean_db):
    """Verify ordering a non-existent product ID returns HTTP 404."""
    payload = {
        "product_id": 9999,
        "quantity": 1,
        "customer_email": "buyer@test.org"
    }
    response = api_client.post("api/v1/orders", json_data=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_create_order_insufficient_stock_fails(api_client, clean_db, test_product):
    """Verify ordering quantity greater than stock returns HTTP 400."""
    payload = {
        "product_id": test_product["id"],
        "quantity": test_product["stock"] + 1, # more than available
        "customer_email": "buyer@test.org"
    }
    response = api_client.post("api/v1/orders", json_data=payload)
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]

@pytest.mark.parametrize("invalid_email", [
    "plainaddress",
    "#@%^%#$@#$@#.com",
    "@example.com",
    "Joe Smith email@example.com",
    "email.example.com",
    "email@example@example.com"
])
def test_create_order_invalid_email_fails(api_client, clean_db, test_product, invalid_email):
    """Verify order creation fails with HTTP 422 if email format is invalid."""
    payload = {
        "product_id": test_product["id"],
        "quantity": 1,
        "customer_email": invalid_email
    }
    response = api_client.post("api/v1/orders", json_data=payload)
    assert response.status_code == 422

def test_create_order_negative_quantity_fails(api_client, clean_db, test_product):
    """Verify order creation fails with HTTP 422 if quantity is <= 0."""
    payload = {
        "product_id": test_product["id"],
        "quantity": 0,
        "customer_email": "buyer@test.org"
    }
    response = api_client.post("api/v1/orders", json_data=payload)
    assert response.status_code == 422
