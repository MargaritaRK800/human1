import requests


def find_business(ll):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
    search_params = {
        "apikey": api_key,
        "lang": "ru_RU",
        "ll": ll,
        "spn": "0.001,0.001",
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)
    if not response:
        raise RuntimeError(
            """Ошибка выполнения запроса:
            {request}
            Http статус: {status} ({reason})""".format(
                request=search_api_server, status=response.status_code, reason=response.reason))

    # Преобразуем ответ в json-объект
    json_response = response.json()

    # Получаем первую найденную организацию.
    organizations = json_response["features"]
    return organizations[0] if organizations else None
