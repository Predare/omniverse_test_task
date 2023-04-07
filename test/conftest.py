import pytest
import requests
import uuid


@pytest.fixture(scope="function")
def json_web_token():
    url = 'https://testers-task.omniversegames.ru/login'
    body = {'username': 'example_user', 'password': 'example_password'}
    response = requests.post(url, json=body)
    responseJson = response.json()
    return responseJson['access_token']


@pytest.fixture(scope="function")
def start_battle(json_web_token):
    url = 'https://testers-task.omniversegames.ru/battle/start'
    usersUUID = [str(uuid.uuid4()), str(uuid.uuid4())]
    headers = {'Authorization': 'Bearer {0}'.format(json_web_token)}
    body = {'users': usersUUID}

    response = requests.post(url, json=body, headers=headers)
    responseJson = response.json()

    return {
        'uuid1': usersUUID[0],
        'uuid2': usersUUID[1],
        'battle_id': responseJson['battle_id']
    }


@pytest.fixture(scope="function", params=[lambda url, headers, json:
                                          requests.delete(
                                              url, headers=headers),
                                          lambda url, headers, json:
                                          requests.options(
                                              url, headers=headers),
                                          lambda url, headers, json:
                                          requests.head(url, headers=headers),
                                          lambda url, headers, json:
                                          requests.put(
                                              url, headers=headers, json=json),
                                          lambda url, headers, json:
                                          requests.patch(
                                              url, headers=headers, json=json),
                                          lambda url, headers, json:
                                          requests.get(
                                              url, headers=headers, json=json),
                                          ])
def http_method(request):
    return request.param
