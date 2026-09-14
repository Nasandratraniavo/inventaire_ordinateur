import requests
from hardware import get_all_specifications


API_URL = "http://127.0.0.1:8000/api/computers"


specifications = get_all_specifications()

response = requests.post(
    API_URL,
    json=specifications,
    timeout=10
)

print("Code HTTP :", response.status_code)
print("Réponse :", response.json())