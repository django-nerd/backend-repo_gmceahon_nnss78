"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Add your own schemas here:
# --------------------------------------------------

class Trip(BaseModel):
    """Bus trips between cities on a specific date"""
    from_city: str = Field(..., description="Origin city")
    to_city: str = Field(..., description="Destination city")
    date: str = Field(..., description="Trip date in YYYY-MM-DD")
    bus_operator: str = Field(..., description="Bus company name")
    departure_time: str = Field(..., description="24h time HH:MM")
    arrival_time: str = Field(..., description="24h time HH:MM")
    price: float = Field(..., ge=0, description="Ticket price")
    seats_total: int = Field(..., ge=1, description="Total seats")
    seats_available: int = Field(..., ge=0, description="Available seats")
    amenities: List[str] = Field(default_factory=list, description="Amenities list")

class Booking(BaseModel):
    """Bookings for a given trip"""
    trip_id: str = Field(..., description="Trip document ID")
    passenger_name: str = Field(...)
    passenger_email: EmailStr = Field(...)
    seats: int = Field(1, ge=1, le=6, description="Number of seats")
    status: str = Field("confirmed", description="Booking status")
