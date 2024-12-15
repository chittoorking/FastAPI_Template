from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
import pytest

# Override database dependency for testing
def override_get_db():
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

# Setup and teardown for each test
@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Create all tables before each test
    Base.metadata.create_all(bind=engine)
    
    # Run the test
    yield
    
    # Drop all tables after the test
    Base.metadata.drop_all(bind=engine)

# Test creating a product
def test_create_product():
    product_data = {
        "name": "Test Product",
        "description": "A test product",
        "price": 19.99,
        "category": "Test Category",
        "stock_quantity": 100
    }
    
    response = client.post("/products/", json=product_data)
    assert response.status_code == 201
    created_product = response.json()
    assert created_product["name"] == product_data["name"]
    assert "id" in created_product

# Test reading products
def test_read_products():
    # Create some test products first
    product_data = {
        "name": "Test Product",
        "description": "A test product",
        "price": 19.99,
        "category": "Test Category",
        "stock_quantity": 100
    }
    client.post("/products/", json=product_data)
    
    # Read products
    response = client.get("/products/")
    assert response.status_code == 200
    products = response.json()
    assert len(products) > 0

# Test updating a product
def test_update_product():
    # Create a product first
    product_data = {
        "name": "Original Product",
        "description": "Original description",
        "price": 19.99,
        "category": "Test Category",
        "stock_quantity": 100
    }
    create_response = client.post("/products/", json=product_data)
    created_product = create_response.json()
    
    # Update the product
    update_data = {
        "name": "Updated Product",
        "price": 29.99
    }
    update_response = client.put(f"/products/{created_product['id']}", json=update_data)
    
    assert update_response.status_code == 200
    updated_product = update_response.json()
    assert updated_product["name"] == "Updated Product"
    assert updated_product["price"] == 29.99

# Test deleting a product
def test_delete_product():
    # Create a product first
    product_data = {
        "name": "Product to Delete",
        "description": "Will be deleted",
        "price": 19.99,
        "category": "Test Category",
        "stock_quantity": 100
    }
    create_response = client.post("/products/", json=product_data)
    created_product = create_response.json()
    
    # Delete the product
    delete_response = client.delete(f"/products/{created_product['id']}")
    assert delete_response.status_code == 204
    
    # Verify product is deleted
    get_response = client.get(f"/products/{created_product['id']}")
    assert get_response.status_code == 404