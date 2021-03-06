from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from ..models import Team, Board, Column, Task, Subtask
from main.helpers.user_helper import UserHelper
from main.helpers.auth_helper import AuthHelper


class CreateTaskTests(APITestCase):
    endpoint = '/tasks/'

    def setUp(self):
        team = Team.objects.create()
        board = Board.objects.create(team=team)
        self.column = Column.objects.create(board=board, order=0)

        user_helper = UserHelper(team)
        self.member = user_helper.create_user()
        self.admin = user_helper.create_user(is_admin=True)

        wrong_user_helper = UserHelper(Team.objects.create())
        self.wrong_admin = wrong_user_helper.create_user(is_admin=True)

    def help_test_success(self, response_data, status_code, request_data):
        self.assertEqual(status_code, 201)
        self.assertEqual(response_data.get('msg'), 'Task creation successful.')
        task_id = response_data.get('task_id')
        self.assertTrue(task_id)
        task = Task.objects.get(id=task_id)
        self.assertEqual(task.title, request_data.get('title'))
        self.assertEqual(task.description, request_data.get('description'))
        self.assertEqual(task.column.id, request_data.get('column'))
        self.assertEqual(task.order, 0)

    def test_success(self):
        initial_count = Task.objects.count()
        request_data = {'title': 'Some Task',
                        'description': 'Lorem ipsum dolor sit amet',
                        'column': self.column.id}
        response = self.client.post(self.endpoint,
                                    request_data,
                                    format='json',
                                    HTTP_AUTH_USER=self.admin['username'],
                                    HTTP_AUTH_TOKEN=self.admin['token'])
        self.help_test_success(response.data,
                               response.status_code,
                               request_data)
        self.assertEqual(Task.objects.count(), initial_count + 1)

    def test_success_without_description(self):
        initial_count = Task.objects.count()
        request_data = {'title': 'Some Task',
                        'description': '',
                        'column': self.column.id}
        response = self.client.post(self.endpoint,
                                    request_data,
                                    HTTP_AUTH_USER=self.admin['username'],
                                    HTTP_AUTH_TOKEN=self.admin['token'])
        self.help_test_success(response.data,
                               response.status_code,
                               request_data)
        self.assertEqual(Task.objects.count(), initial_count + 1)

    def test_success_with_subtasks(self):
        initial_count = Task.objects.count()
        request_data = {'title': 'Some Task',
                        'description': 'Lorem ipsum dolor sit amet',
                        'column': self.column.id,
                        'subtasks': ['Do something',
                                     'Do some other thing']}
        response = self.client.post(self.endpoint,
                                    request_data,
                                    format='json',
                                    HTTP_AUTH_USER=self.admin['username'],
                                    HTTP_AUTH_TOKEN=self.admin['token'])
        self.help_test_success(response.data,
                               response.status_code,
                               request_data)
        subtasks = Subtask.objects.filter(task=response.data.get('task_id'))
        self.assertEqual(subtasks.count(), len(request_data.get('subtasks')))
        self.assertEqual(Task.objects.count(), initial_count + 1)

    def test_title_blank(self):
        initial_count = Task.objects.count()
        request = {'title': '',
                   'description': 'Lorem ipsum dolor sit amet',
                   'column': self.column.id}
        response = self.client.post(self.endpoint,
                                    request,
                                    HTTP_AUTH_USER=self.admin['username'],
                                    HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'title': [ErrorDetail(string='Title cannot be blank.',
                                  code='blank')]
        })
        self.assertEqual(Task.objects.count(), initial_count)

    def test_title_max_length(self):
        initial_count = Task.objects.count()
        request_data = {
            'title': 'foooooooooooooooooooooooooooooooooooooooooooooooooooooo'
                     'ooooooooooooooooooooooooooooooooooooooooooooooooooooooo',
            'description': 'Lorem ipsum dolor sit amet',
            'column': self.column.id
        }
        response = self.client.post(self.endpoint,
                                    request_data,
                                    HTTP_AUTH_USER=self.admin['username'],
                                    HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'title': [
                ErrorDetail(
                    string='Title cannot be longer than 50 characters.',
                    code='max_length'
                ),
            ]
        })
        self.assertEqual(Task.objects.count(), initial_count)

    def test_subtask_max_length(self):
        initial_count = Task.objects.count()
        request_data = {
            'title': 'Some Task',
            'description': 'Lorem ipsum dolor sit amet',
            'column': self.column.id,
            'subtasks': [
                'foooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo'
                'ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo'
            ]
        }
        response = self.client.post(self.endpoint,
                                    request_data,
                                    format='json',
                                    HTTP_AUTH_USER=self.admin['username'],
                                    HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'subtask': [{
                'title': [ErrorDetail(
                    string='Subtask titles cannot be longer than 50 '
                           'characters.',
                    code='max_length'
                )],
            }]
        })
        self.assertEqual(Task.objects.count(), initial_count)

    def test_column_blank(self):
        initial_count = Task.objects.count()
        request_data = {'title': 'Some Task',
                        'description': 'Lorem ipsum dolor sit amet',
                        'column': ''}
        response = self.client.post(self.endpoint,
                                    request_data,
                                    HTTP_AUTH_USER=self.admin['username'],
                                    HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'column': [ErrorDetail(string='Column cannot be null.',
                                   code='null')]
        })
        self.assertEqual(Task.objects.count(), initial_count)

    def test_auth_token_empty(self):
        initial_count = Task.objects.count()
        request_data = {'title': 'Some Task',
                        'description': 'Lorem ipsum dolor sit amet',
                        'column': self.column.id}
        response = self.client.post(self.endpoint,
                                    request_data,
                                    HTTP_AUTH_USER=self.admin['username'],
                                    HTTP_AUTH_TOKEN='')
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHENTICATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHENTICATION_ERROR.detail)
        self.assertEqual(Task.objects.count(), initial_count)

    def test_auth_token_invalid(self):
        initial_count = Task.objects.count()
        request_data = {'title': 'Some Task',
                        'description': 'Lorem ipsum dolor sit amet',
                        'column': self.column.id}
        response = self.client.post(self.endpoint,
                                    request_data,
                                    HTTP_AUTH_USER=self.admin['username'],
                                    HTTP_AUTH_TOKEN='ASDKFJ!FJ_012rjpiwajfosi')
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHENTICATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHENTICATION_ERROR.detail)
        self.assertEqual(Task.objects.count(), initial_count)

    def test_auth_user_blank(self):
        initial_count = Task.objects.count()
        request_data = {'title': 'Some Task',
                        'description': 'Lorem ipsum dolor sit amet',
                        'column': self.column.id}
        response = self.client.post(self.endpoint,
                                    request_data,
                                    HTTP_AUTH_USER='',
                                    HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHENTICATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHENTICATION_ERROR.detail)
        self.assertEqual(Task.objects.count(), initial_count)

    def test_auth_user_invalid(self):
        initial_count = Task.objects.count()
        request_data = {'title': 'Some Task',
                        'description': 'Lorem ipsum dolor sit amet',
                        'column': self.column.id}
        response = self.client.post(self.endpoint,
                                    request_data,
                                    HTTP_AUTH_USER='invalidio',
                                    HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHENTICATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHENTICATION_ERROR.detail)
        self.assertEqual(Task.objects.count(), initial_count)

    def test_wrong_team(self):
        initial_count = Task.objects.count()
        request_data = {'title': 'Some Task',
                        'description': 'Lorem ipsum dolor sit amet',
                        'column': self.column.id}
        response = self.client.post(self.endpoint,
                                    request_data,
                                    HTTP_AUTH_USER=self.wrong_admin['username'],
                                    HTTP_AUTH_TOKEN=self.wrong_admin['token'])
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHORIZATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHORIZATION_ERROR.detail)
        self.assertEqual(Task.objects.count(), initial_count)

    def test_unauthorized(self):
        initial_count = Task.objects.count()
        request_data = {'title': 'Some Task',
                        'description': 'Lorem ipsum dolor sit amet',
                        'column': self.column.id}
        response = self.client.post(self.endpoint,
                                    request_data,
                                    HTTP_AUTH_USER=self.member['username'],
                                    HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHORIZATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHORIZATION_ERROR.detail)
        self.assertEqual(Task.objects.count(), initial_count)
