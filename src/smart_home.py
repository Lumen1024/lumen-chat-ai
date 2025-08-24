import base64
import requests

CLIENT_ID = "2f7e2fc4180a41d98667dbe1c60c86e6"
CLIENT_SECRET = "e179c5b0a81c44138007e8a50749c86c"

TOKEN = "y0__xClyIXzARiUzjkgnvyPjBQ8Rs5POpNWfjZBRTH3-6dtthZqMQ"
LIGHT_IDS = [
    "0cc7ca64-a860-417e-aec9-b6a584d12f27",
    "9b2c533e-634c-4d66-b87f-4a98a4b5b30d",
    "fb2c4501-2868-4676-be51-216ab2d5989d",
]


def yandex_iot_power_change(device_id: str, state: bool, token: str) -> bool:
    """
    Изменяет состояние питания устройства через Yandex IoT API

    Args:
        device_id: ID устройства в Яндекс Умном доме
        state: Желаемое состояние (True - включить, False - выключить)
        token: OAuth токен для авторизации

    Returns:
        bool: True если успешно, False если ошибка
    """
    url = "https://api.iot.yandex.net/v1.0/devices/actions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    data = {
        "devices": [
            {
                "id": device_id,
                "actions": [
                    {
                        "type": "devices.capabilities.on_off",
                        "state": {"instance": "on", "value": state},
                    }
                ],
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Генерирует исключение для HTTP ошибок

        result = response.json()
        return result.get("status") == "ok"

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при изменении состояния устройства: {e}")
        return False
    except ValueError as e:
        print(f"Ошибка парсинга JSON ответа: {e}")
        return False


def getToken(code):
    # Формируем Basic Auth заголовок
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    base64_credentials = base64.b64encode(credentials.encode()).decode()

    # Запрос на получение токена
    url = "https://oauth.yandex.ru/token"
    headers = {
        "Authorization": f"Basic {base64_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
    }

    response = requests.post(url, headers=headers, data=data)
    token_data = response.json()

    if "access_token" in token_data:
        access_token = token_data["access_token"]
        print(token_data)
        return access_token
    else:
        print("Ошибка получения токена:", token_data)


def get_devices(token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        response = requests.get(
            "https://api.iot.yandex.net/v1.0/user/info",
            headers=headers,
        )

        if response.status_code == 200:
            return response.json()  # Возвращаем данные
        else:
            print(f"Ошибка {response.status_code}: {response.text}")
            return None

    except Exception as e:
        print(f"Ошибка запроса: {e}")
        return None
