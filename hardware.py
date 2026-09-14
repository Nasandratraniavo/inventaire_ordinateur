import subprocess
import json
import psutil
import platform


def run_powershell(command):
    """
    Exécute une commande PowerShell et retourne le résultat.
    """
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        if result.returncode != 0:
            return None

        return result.stdout.strip()

    except Exception as e:
        print(f"Erreur PowerShell : {e}")
        return None


def get_computer_info():
    """
    Récupère la marque et le modèle de l'ordinateur.
    """

    command = """
    Get-CimInstance Win32_ComputerSystem |
    Select-Object Manufacturer, Model |
    ConvertTo-Json
    """

    result = run_powershell(command)

    if not result:
        return {
            "brand": "Inconnu",
            "model": "Inconnu"
        }

    try:
        data = json.loads(result)

        return {
            "brand": data.get("Manufacturer", "Inconnu"),
            "model": data.get("Model", "Inconnu")
        }

    except json.JSONDecodeError:
        return {
            "brand": "Inconnu",
            "model": "Inconnu"
        }


def get_serial_number():
    """
    Récupère le numéro de série du BIOS.
    """

    command = """
    Get-CimInstance Win32_BIOS |
    Select-Object -ExpandProperty SerialNumber
    """

    result = run_powershell(command)

    return result if result else "Inconnu"


def get_cpu():
    """
    Récupère le modèle du processeur.
    """

    command = """
    Get-CimInstance Win32_Processor |
    Select-Object -ExpandProperty Name
    """

    result = run_powershell(command)

    return result if result else "Inconnu"


def get_gpu():
    """
    Récupère les GPU présents sur l'ordinateur.
    """

    command = """
    Get-CimInstance Win32_VideoController |
    Select-Object -ExpandProperty Name
    """

    result = run_powershell(command)

    if not result:
        return []

    gpu_list = [
        gpu.strip()
        for gpu in result.splitlines()
        if gpu.strip()
    ]

    return gpu_list


def get_ram():
    """
    Récupère la quantité totale de RAM.
    """

    ram = psutil.virtual_memory()

    ram_gb = ram.total / 1_000_000_000

    return round(ram_gb, 0)


def get_storage():
    """
    Récupère les disques physiques :
    - type (SSD/HDD)
    - capacité
    """

    command = """
    Get-PhysicalDisk |
    Select-Object FriendlyName, MediaType, Size |
    ConvertTo-Json
    """

    result = run_powershell(command)

    if not result:
        return []

    try:
        data = json.loads(result)

        # Lorsqu'il n'y a qu'un seul disque,
        # PowerShell peut retourner un objet au lieu d'une liste.
        if isinstance(data, dict):
            data = [data]

        storage_list = []

        for disk in data:

            size_bytes = disk.get("Size", 0)

            if size_bytes:
                size_gb = round(size_bytes / 1_000_000_000, 0)
            else:
                size_gb = 0

            storage_list.append({
                "type": disk.get("MediaType", "Unknown"),
                "capacity_gb": size_gb
            })

        return storage_list

    except json.JSONDecodeError:
        return []


def get_all_specifications():
    """
    Récupère toutes les spécifications de l'ordinateur.
    """

    computer = get_computer_info()

    specifications = {
        "serial_number": get_serial_number(),

        "brand": computer["brand"],

        "model": computer["model"],

        "cpu": get_cpu(),

        "gpu": get_gpu(),

        "ram_gb": get_ram(),

        "storage": get_storage()
    }

    return specifications


def display_specifications(specifications):
    """
    Affiche les informations de manière lisible.
    """

    print(f"Numéro de série : {specifications['serial_number']}")
    print(f"Marque          : {specifications['brand']}")
    print(f"Modèle          : {specifications['model']}")
    print(f"CPU             : {specifications['cpu']}")
    print("GPU :")

    if specifications["gpu"]:
        for gpu in specifications["gpu"]:
            print(f"  - {gpu}")
    else:
        print("  Aucun GPU détecté")

    print(f"RAM             : {specifications['ram_gb']} GB")

    print("Stockage :")

    if specifications["storage"]:

        for disk in specifications["storage"]:
            print(
                f"  - {disk['type']} | "
                f"{disk['capacity_gb']} GB"
            )

    else:
        print("  Aucun disque détecté")

def save_to_json(specifications, filename="computer_inventory.json"):
    """
    Sauvegarde les spécifications dans un fichier JSON.
    """

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(
            specifications,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(f"\nDonnées sauvegardées dans : {filename}")


if __name__ == "__main__":
    specifications = get_all_specifications()
    save_to_json(specifications)