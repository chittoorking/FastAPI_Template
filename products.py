from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import Product, get_db
from app.schemas import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

# Create a new product
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Get all products
@router.get("/", response_model=List[ProductResponse])
def read_products(
    skip: int = 0, 
    limit: int = 100, 
    category: str = None, 
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    # Optional category filtering
    if category:
        query = query.filter(Product.category == category)
    
    return query.offset(skip).limit(limit).all()

# Get a specific product by ID
@router.get("/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Update a product (full or partial update)
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int, 
    product: ProductUpdate, 
    db: Session = Depends(get_db)
):
    # Find the existing product
    db_product = db.query(Product).filter(Product.id == product_id).first()
    
    # Check if product exists
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update only provided fields
    update_data = product.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

# Delete a product
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    # Find the product
    product = db.query(Product).filter(Product.id == product_id).first()
    
    # Check if product exists
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete the product
    db.delete(product)
    db.commit()
    return None

# Batch operations
@router.post("/bulk", response_model=List[ProductResponse])
def create_multiple_products(
    products: List[ProductCreate], 
    db: Session = Depends(get_db)
):
    db_products = [Product(**product.dict()) for product in products]
    db.add_all(db_products)
    db.commit()
    
    # Refresh to get the IDs
    for product in db_products:
        db.refresh(product)
    
    return db_products