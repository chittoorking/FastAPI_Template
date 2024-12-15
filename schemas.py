from pydantic import BaseModel, Field
from typing import Optional

# Product request schema
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=2, max_length=50)
    stock_quantity: int = Field(..., ge=0)

# Product response schema
class ProductResponse(ProductCreate):
    id: int

    class Config:
        orm_mode = True

# Partial update schema
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    stock_quantity: Optional[int] = None