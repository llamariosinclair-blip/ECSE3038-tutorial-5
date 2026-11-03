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
