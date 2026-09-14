import os
import requests

from hardware import get_all_specifications


API_URL = "https://inventaire-ordinateur.onrender.com/api/computers"

API_KEY = os.getenv("API_KEY")


def main():
    print("=" * 40)
    print("       INVENTAIRE ORDINATEUR")
    print("=" * 40)
    print()

    # Vérification de la clé API
    if not API_KEY:
        print("✗ API_KEY non configurée.")
        print("Contactez l'administrateur.")
        return

    # Collecte des informations
    print("Collecte des informations...")

    try:
        specifications = get_all_specifications()

        print("✓ Informations collectées")
        print()

    except Exception as e:
        print("✗ Erreur lors de la collecte des informations.")
        print(f"Détail : {e}")
        return

    # Envoi vers l'API
    print("Envoi des informations au serveur...")

    headers = {
        "X-API-Key": API_KEY
    }

    try:
        response = requests.post(
            API_URL,
            json=specifications,
            headers=headers,
            timeout=30
        )

    except requests.exceptions.Timeout:
        print("✗ Le serveur ne répond pas.")
        print("Vérifiez votre connexion Internet et réessayez.")
        return

    except requests.exceptions.ConnectionError:
        print("✗ Impossible de contacter le serveur.")
        print("Vérifiez votre connexion Internet.")
        return

    except requests.exceptions.RequestException as e:
        print("✗ Une erreur réseau est survenue.")
        print(f"Détail : {e}")
        return

    # Analyse de la réponse du serveur
    if response.status_code == 200:
        print("✓ Inventaire envoyé avec succès.")

    elif response.status_code == 401:
        print("✗ Clé API invalide.")

    elif response.status_code >= 500:
        print("✗ Erreur du serveur.")
        print("Veuillez réessayer plus tard.")

    else:
        print(f"✗ Le serveur a retourné le code {response.status_code}.")

    print("Vous pouvez fermer cette fenêtre !!!")


if __name__ == "__main__":
    main()