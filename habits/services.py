import requests


def send_message(token, chat_id, message):  # Функция интеграции с Телеграмм
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post(url, data=data)
    return response.json()
