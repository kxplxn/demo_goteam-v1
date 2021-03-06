from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from main.models import Team
from main.helpers.user_helper import UserHelper


class LoginTests(APITestCase):
    endpoint = '/login/'

    def setUp(self):
        user_helper = UserHelper(Team.objects.create())
        self.user = user_helper.create_user()

    def test_success(self):
        request_data = {'username': self.user['username'],
                        'password': self.user['password_raw']}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('msg'), 'Login successful.')
        self.assertEqual(response.data.get('username'), self.user['username'])
        self.assertEqual(response.data.get('teamId'), self.user['team'].id)
        self.assertEqual(response.data.get('isAdmin'), self.user['is_admin'])
        self.assertTrue(response.data.get('token'))

    def test_username_blank(self):
        request_data = {'username': '', 'password': self.user['password_raw']}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'username': [ErrorDetail(string='Username cannot be null.',
                                     code='null')]
        })

    def test_username_max_length(self):
        request_data = {'username': 'fooooooooooooooooooooooooooooooooooo',
                        'password': self.user['password_raw']}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'username': [ErrorDetail(string='Invalid username.',
                                     code='does_not_exist')]
        })

    # noinspection DuplicatedCode
    def test_password_max_length(self):
        password = '''
            barbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarb
            arbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarba
            rbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarbar
            barbarbarbarbarbarbarbarbarbarbarbarbarbarbarbarba
        '''
        request_data = {'username': self.user['username'], 'password': password}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'password': [
                ErrorDetail(
                    string='Password cannot be longer than 255 characters.',
                    code='max_length'
                )
            ]
        })

    def test_password_blank(self):
        request_data = {'username': self.user['username'], 'password': ''}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'password': [ErrorDetail(string='Password cannot be empty.',
                                     code='blank')]
        })

    def test_username_invalid(self):
        request_data = {'username': 'invalidusername',
                        'password': self.user['password_raw']}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'username': [ErrorDetail(string='Invalid username.',
                                     code='does_not_exist')]
        })

    def test_password_invalid(self):
        request_data = {'username': self.user['username'],
                        'password': 'invalidpassword'}
        response = self.client.post(self.endpoint, request_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'password': ErrorDetail(string='Invalid password.', code='invalid')
        })
