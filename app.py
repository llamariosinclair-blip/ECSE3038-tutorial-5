import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["ecse3038"]
devices = db["tutorial5"]

app = FastAPI()

class Device(BaseModel):
    name: str
    room: str
    temp: float
    online: bool

# Task 1: GET all devices
@app.get("/devices", status_code=status.HTTP_200_OK)
def get_all_devices():
    # Return all devices, excluding the MongoDB-specific _id field
    return list(devices.find({}, {"_id": 0}))

# Task 2: GET one device
@app.get("/devices/{name}", status_code=status.HTTP_200_OK)
def get_device(name: str):
    device = devices.find_one({"name": name}, {"_id": 0})
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device

# Task 3: POST create device
@app.post("/devices", status_code=status.HTTP_201_CREATED)
def create_device(device: Device):
    # Optional but recommended: Check if device already exists
    if devices.find_one({"name": device.name}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Device already exists")
    
    # Insert document (using model_dump() for Pydantic v2; use dict() if on v1)
    devices.insert_one(device.model_dump())
    return device

# Task 4: PUT update or create device
@app.put("/devices/{name}")
def put_device(name: str, device: Device, response: Response):
    # Enforce that the URI name matches the body payload name
    if name != device.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="The name in the URL must match the name in the body."
        )
    
    # replace_one with upsert=True replaces the existing doc or creates a new one
    result = devices.replace_one({"name": name}, device.model_dump(), upsert=True)
    
    # RFC 9110 §9.3.4: Return 201 Created if a new resource was created, otherwise 200 OK
    if result.upserted_id:
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_200_OK
        
    return device

# Task 5: DELETE device
@app.delete("/devices/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(name: str):
    result = devices.delete_one({"name": name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    # 204 No Content requires no body to be returned
    return None