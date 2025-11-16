import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents

app = FastAPI(title="RedBus Clone API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "RedBus Clone Backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "Unknown"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Schemas import (for type hints)
from schemas import Trip, Booking

class SearchQuery(BaseModel):
    from_city: str
    to_city: str
    date: str  # YYYY-MM-DD

@app.post("/api/search")
async def search_trips(payload: SearchQuery):
    # Query DB for trips matching criteria
    filters = {
        "from_city": payload.from_city,
        "to_city": payload.to_city,
        "date": payload.date,
    }
    trips = get_documents("trip", filters, limit=100)
    results = []
    for t in trips:
        t_id = str(t.pop("_id", ""))
        t_dict = {**t, "id": t_id}
        results.append(t_dict)
    return results

class SeedTrip(BaseModel):
    from_city: str
    to_city: str
    date: str
    bus_operator: str
    departure_time: str
    arrival_time: str
    price: float
    seats_total: int
    seats_available: int
    amenities: Optional[List[str]] = []

@app.post("/api/admin/seed", status_code=201)
async def seed_trip(payload: SeedTrip):
    # Insert a new trip
    trip_id = create_document("trip", payload.model_dump())
    return {"inserted_id": trip_id}

class BookingRequest(BaseModel):
    trip_id: str
    passenger_name: str
    passenger_email: str
    seats: int

@app.post("/api/book", status_code=201)
async def create_booking(payload: BookingRequest):
    # Validate trip exists and seats available
    try:
        obj_id = ObjectId(payload.trip_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid trip_id")

    trip = db["trip"].find_one({"_id": obj_id})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip.get("seats_available", 0) < payload.seats:
        raise HTTPException(status_code=400, detail="Not enough seats available")

    # Create booking
    booking_data = {
        "trip_id": payload.trip_id,
        "passenger_name": payload.passenger_name,
        "passenger_email": payload.passenger_email,
        "seats": payload.seats,
        "status": "confirmed",
    }
    booking_id = create_document("booking", booking_data)

    # Update seats
    db["trip"].update_one({"_id": obj_id}, {"$inc": {"seats_available": -payload.seats}})

    return {"booking_id": booking_id, "message": "Booking confirmed"}

@app.get("/api/trips/{trip_id}")
async def get_trip(trip_id: str):
    try:
        obj_id = ObjectId(trip_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid trip_id")
    doc = db["trip"].find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Trip not found")
    doc["_id"] = str(doc["_id"])
    return doc

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
