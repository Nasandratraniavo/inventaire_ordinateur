from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from google_sheets import add_computer

app = FastAPI()

class Storage(BaseModel):
    type: str
    capacity_gb: float

class Computer(BaseModel):
    serial_number: str
    brand: str
    model: str
    cpu: str
    gpu: List[str]
    ram_gb: float
    storage: List[Storage]

@app.get("/")
def home():
    return {
        "message": "API Computer Inventory opérationnelle"
    }


@app.post("/api/computers")
def receive_computer(computer: Computer):

    add_computer(computer)

    return {
        "status": "success",
        "message": "Ordinateur reçu avec succès"
    }