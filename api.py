from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List
from google_sheets import add_computer
import os

app = FastAPI()

class Storage(BaseModel):
    type: str
    interface: str
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
def receive_computer(
    computer: Computer,
    x_api_key: str | None = Header(default=None)
):

    api_key = os.getenv("API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="API_KEY non configurée sur le serveur"
        )

    if x_api_key != api_key:
        raise HTTPException(
            status_code=401,
            detail="Clé API invalide"
        )

    resultat = add_computer(computer)

    if resultat == "duplicate":
        raise HTTPException(
            status_code=409,
            detail=f"Le numéro de série {computer.serial_number} existe déjà."
        )

    elif resultat == "missing_serial":
        raise HTTPException(
            status_code=400,
            detail="Le numéro de série est manquant."
        )

    elif resultat != "success":
        raise HTTPException(
            status_code=500,
            detail="Impossible d'enregistrer l'ordinateur."
        )

    return {
        "status": "success",
        "message": "Ordinateur reçu avec succès"
    }