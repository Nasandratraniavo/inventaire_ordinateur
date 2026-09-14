import gspread
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1


# 1. Autorisations nécessaires
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]


# 2. Charger les credentials
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

    gpu = ", ".join(computer.gpu) if computer.gpu else ""

    disktype = computer.storage[0].type
    diskcapacity = computer.storage[0].capacity_gb

    # Lire les en-têtes de la ligne 4
    headers = worksheet.row_values(4)

    # Créer une ligne vide avec le même nombre de colonnes
    row = [""] * len(headers)

    # Correspondance entre les en-têtes et les données
    data = {
        "Numéro de série": computer.serial_number,
        "Marque": computer.brand,
        "Modèle": computer.model,
        "Processeur": computer.cpu,
        "Graphique": gpu,
        "RAM (Go)": computer.ram_gb,
        "Type Stockage": disktype,
        "Capacité Stockage (Go)": diskcapacity,
    }

    # Remplir uniquement les colonnes dont on connaît l'en-tête
    for header, value in data.items():

        if header in headers:
            column_index = headers.index(header)
            row[column_index] = value

    # Ajouter la nouvelle ligne
    # worksheet.append_row(row)

    # ---------------------------------------
    # Chercher la prochaine ligne disponible
    # ---------------------------------------

    serial_column = headers.index("Numéro de série") + 1

    serial_values = worksheet.col_values(serial_column)

    # Les données commencent à la ligne 5
    next_row = max(5, len(serial_values) + 1)

    # ---------------------------------------
    # Écrire la ligne
    # ---------------------------------------

    start_cell = rowcol_to_a1(next_row, 1)
    end_cell = rowcol_to_a1(next_row, len(row))

    worksheet.update(
        f"{start_cell}:{end_cell}",
        [row]
    )

    print(f"Ordinateur ajouté à la ligne {next_row}")