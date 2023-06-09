import pytest
import requests
import uuid
import utils

BASE_URL = 'https://testers-task.omniversegames.ru/'


class TestLogin:
    url = ''.join((BASE_URL, 'login'))

    def test_positive_scenario(self):
        body = {'username': 'example_user', 'password': 'example_password'}
        response = requests.post(self.url, json=body)

        assert response.status_code == requests.codes.ok
        assert response.headers.get('content-type') == 'application/json'

        responseJson = response.json()
        assert type(responseJson['access_token']) is str
        assert type(responseJson['token_type']) is str

        assert responseJson['token_type'] == 'bearer'

    @pytest.mark.parametrize("login",
                             ['sdfsdf',
                              'fdssdf234123__43432`____"___fdsf'
                              ])
    @pytest.mark.parametrize("password",
                             ['sadfsdfdsf',
                              'sfdf_`_"____`"\'__sd'
                              ])
    def test_wrong_data_scenario(self, login, password):
        body = {'username': login, 'password': password}
        response = requests.post(self.url, json=body)
        assert response.status_code == requests.codes.unauthorized

    def test_forbidden_methods(self, http_method):
        body = {'username': 'example_user', 'password': 'example_password'}
        response = http_method(url=self.url, headers={}, json=body)
        assert response.status_code == requests.codes.not_allowed


class TestStartBattle:
    url = ''.join((BASE_URL, 'battle/start'))

    def test_positive_scenario(self, json_web_token):
        usersUUID = [str(uuid.uuid4()), str(uuid.uuid4())]
        headers = {'Authorization': 'Bearer {0}'.format(json_web_token)}
        body = {'users': usersUUID}

        response = requests.post(self.url, json=body, headers=headers)
        assert response.status_code == requests.codes.ok
        assert response.headers.get('content-type') == 'application/json'

        responseJson = response.json()
        assert uuid.UUID(responseJson['battle_id'])

    @pytest.mark.parametrize("uuid1",
                             ['sdfsdf',
                              'fdssdf234123__43432`____"___fdsf'
                              ])
    @pytest.mark.parametrize("uuid2",
                             ['sdfsdf',
                              'fdssdf234123__43432`____"___fdsf'
                              ])
    def test_wrong_data_scenario(self, json_web_token, uuid1, uuid2):
        usersUUID = [uuid1, uuid2]
        headers = {'Authorization': 'Bearer {0}'.format(json_web_token)}
        body = {'users': usersUUID}

        response = requests.post(self.url, json=body, headers=headers)
        assert response.status_code == requests.codes.unprocessable_entity

    def test_unauthorized_request(self):
        usersUUID = [str(uuid.uuid4()), str(uuid.uuid4())]
        body = {'users': usersUUID}

        response = requests.post(self.url, json=body)
        assert response.status_code == requests.codes.forbidden

    def test_forbidden_methods(self, json_web_token, http_method):
        usersUUID = [str(uuid.uuid4()), str(uuid.uuid4())]
        headers = {'Authorization': 'Bearer {0}'.format(json_web_token)}
        body = {'users': usersUUID}

        response = http_method(url=self.url, headers=headers, json=body)
        assert response.status_code == requests.codes.not_allowed

    def test_wrong_jwt(self):
        usersUUID = [str(uuid.uuid4()), str(uuid.uuid4())]
        headers = {'Authorization': 'Bearer 1231231233'}
        body = {'users': usersUUID}

        response = requests.post(self.url, json=body, headers=headers)
        assert response.status_code == requests.codes.unauthorized


class TestEndBattle:
    url = ''.join((BASE_URL, 'battle/end'))

    def test_positive_scenario(self, json_web_token, start_battle):
        headers = {'Authorization': 'Bearer {0}'.format(json_web_token)}
        uuid1 = {'is_won': str(True).lower()}
        uuid2 = {'is_won': str(False).lower()}
        users = {start_battle['uuid1']: uuid1, start_battle['uuid2']: uuid2}
        body = {
            'battle_id': start_battle['battle_id'],
            'results': users}

        response = requests.post(self.url, headers=headers, json=body)
        assert response.status_code == requests.codes.ok
        assert response.headers.get('content-type') == 'application/json'

        responseJson = response.json()
        assert responseJson['success'] == True
        assert type(responseJson['battle']) is dict

        battle = responseJson['battle']
        assert uuid.UUID(battle['id'])
        assert utils.is_date(battle['started_at'])
        assert utils.is_date(battle['ended_at'])

        userList = list(users)
        assert battle['winner'] == userList[0]
        assert battle['users'] == userList

    def test_wrong_uuid_scenario(self, json_web_token, start_battle):
        headers = {'Authorization': 'Bearer {0}'.format(json_web_token)}
        uuid1 = {'is_won': str(True).lower()}
        uuid2 = {'is_won': str(False).lower()}
        users = {'dsfsdf': uuid1, start_battle['uuid2']: uuid2}
        body = {
            'battle_id': start_battle['battle_id'],
            'results': users}

        response = requests.post(self.url, headers=headers, json=body)
        assert response.status_code == requests.codes.unprocessable_entity

    def test_wrong_user_data_scenario(self, json_web_token, start_battle):
        headers = {'Authorization': 'Bearer {0}'.format(json_web_token)}
        uuid1 = {'is_won': 'Wrong data'}
        uuid2 = {'is_won': str(False).lower()}
        users = {start_battle['uuid1']: uuid1, 'fdfds': uuid2}
        body = {
            'battle_id': start_battle['battle_id'],
            'results': users}

        response = requests.post(self.url, headers=headers, json=body)
        assert response.status_code == requests.codes.unprocessable_entity

    def test_wrong_battle_id_scenario(self, json_web_token, start_battle):
        headers = {'Authorization': 'Bearer {0}'.format(json_web_token)}
        uuid1 = {'is_won': str(True).lower()}
        uuid2 = {'is_won': str(False).lower()}
        users = {start_battle['uuid1']: uuid1, 'fdfds': uuid2}
        body = {
            'battle_id': 'sdfsfd',
            'results': users}

        response = requests.post(self.url, headers=headers, json=body)
        assert response.status_code == requests.codes.unprocessable_entity

    def test_forbidden_methods(self, json_web_token, http_method, start_battle):
        headers = {'Authorization': 'Bearer {0}'.format(json_web_token)}
        uuid1 = {'is_won': str(True).lower()}
        uuid2 = {'is_won': str(False).lower()}
        users = {start_battle['uuid1']: uuid1, start_battle['uuid2']: uuid2}
        body = {
            'battle_id': start_battle['battle_id'],
            'results': users}

        response = http_method(url=self.url, headers=headers, json=body)
        assert response.status_code == requests.codes.not_allowed

    def test_unauthorized_request(self, start_battle):
        uuid1 = {'is_won': str(True).lower()}
        uuid2 = {'is_won': str(False).lower()}
        users = {start_battle['uuid1']: uuid1, start_battle['uuid2']: uuid2}
        body = {
            'battle_id': start_battle['battle_id'],
            'results': users}

        response = requests.post(self.url, json=body)
        assert response.status_code == requests.codes.forbidden

    def test_wrong_jwt(self, start_battle):
        headers = {'Authorization': 'Bearer 1231231233'}
        uuid1 = {'is_won': str(True).lower()}
        uuid2 = {'is_won': str(False).lower()}
        users = {start_battle['uuid1']: uuid1, start_battle['uuid2']: uuid2}
        body = {
            'battle_id': start_battle['battle_id'],
            'results': users}

        response = requests.post(self.url, headers=headers, json=body)
        assert response.status_code == requests.codes.unauthorized
