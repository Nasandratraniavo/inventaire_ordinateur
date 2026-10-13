import gspread
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1
import os
import json
import base64


# 1. Autorisations nécessaires
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]


# 2. Charger les credentials
credentials_base64 = os.getenv("GOOGLE_CREDENTIALS")

if credentials_base64:
    # Cas Render
    credentials_info = json.loads(
        base64.b64decode(credentials_base64).decode("utf-8")
    )

    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=SCOPES
    )

else:
    # Cas local
    credentials = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )


# 3. Authentification auprès de Google
client = gspread.authorize(credentials)


# 4. Ouvrir le Google Sheet
spreadsheet = client.open_by_key("1gcl55MAM-l0cz5zRUEt6njKev3kteaO8sdn1_x7qd8A")


# 5. Sélectionner la première feuille
worksheet = spreadsheet.get_worksheet(2)



def add_computer(computer):

    # Lire les en-têtes de la ligne 4
    headers = worksheet.row_values(4)

    # Vérifier que la colonne Numéro de série existe
    if "Numéro de série" not in headers:
        raise ValueError("Colonne 'Numéro de série' introuvable.")

    # Trouver l'index de la colonne (index Python : commence à 0)
    serial_index = headers.index("Numéro de série")

    # Récupérer les numéros de série déjà enregistrés
    serial_values = worksheet.col_values(serial_index + 1)

    # Numéro de série de l'ordinateur à ajouter
    serial_number = str(computer.serial_number).strip()

    # Vérifier si le numéro existe déjà, à partir de la ligne 5
    existing_serials = {
        value.strip()
        for value in serial_values[4:]
        if value.strip()
    }

    if not serial_number:
        print("Ajout annulé : numéro de série manquant.")
        return "missing_serial"

    if serial_number in existing_serials:
        print(f"Ajout annulé : le numéro de série {serial_number} existe déjà.")
        return "duplicate"

    # Préparer les données
    gpu = ", ".join(computer.gpu) if computer.gpu else ""

    disktype = ", ".join(
        f"{disk.type} {disk.interface}"
        for disk in computer.storage
    )

    diskcapacity = (
        computer.storage[0].capacity_gb
        if computer.storage else ""
    )

    data = {
        "Numéro de série": serial_number,
        "Marque": computer.brand,
        "Modèle": computer.model,
        "Processeur": computer.cpu,
        "Graphique": gpu,
        "RAM (Go)": computer.ram_gb,
        "Type Stockage": disktype,
        "Capacité Stockage (Go)": diskcapacity,
    }

    # Construire une ligne correspondant aux en-têtes
    row = [""] * len(headers)

    for header, value in data.items():
        if header in headers:
            column_index = headers.index(header)
            row[column_index] = value

    # Déterminer la prochaine ligne disponible
    next_row = max(5, len(serial_values) + 1)

    # Écrire la ligne dans Google Sheets
    start_cell = rowcol_to_a1(next_row, 1)
    end_cell = rowcol_to_a1(next_row, len(row))

    worksheet.update(
        f"{start_cell}:{end_cell}",
        [row]
    )

    print(f"Ordinateur ajouté à la ligne {next_row}")
    return "success"