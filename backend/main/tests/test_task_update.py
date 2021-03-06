from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from ..models import Task, Column, Board, Team, User
from main.helpers.user_helper import UserHelper
from main.helpers.auth_helper import AuthHelper


class UpdateTaskTests(APITestCase):
    endpoint = '/tasks/?id='

    def setUp(self):
        team = Team.objects.create()

        user_helper = UserHelper(team)
        self.member = user_helper.create_user()
        self.admin = user_helper.create_user(is_admin=True)
        self.assigned_member = user_helper.create_user()

        wrong_user_helper = UserHelper(Team.objects.create())
        self.wrong_admin = wrong_user_helper.create_user(is_admin=True)

        self.task = Task.objects.create(
            title="Task Title",
            order=0,
            user=User.objects.get(username=self.assigned_member['username']),
            column=Column.objects.create(
                order=0,
                board=Board.objects.create(
                    team=team
                )
            )
        )

    def help_test_success(self, task_id, request_data):
        response = self.client.patch(f'{self.endpoint}{task_id}',
                                     request_data,
                                     format='json',
                                     HTTP_AUTH_USER=self.admin['username'],
                                     HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'msg': 'Task update successful.',
                                         'id': self.task.id})
        self.assertEqual(self.task.id, response.data.get('id'))

    def test_title_success(self):
        request_data = {'title': 'New Title'}
        self.help_test_success(self.task.id, request_data)
        self.assertEqual(Task.objects.get(id=self.task.id).title,
                         request_data.get('title'))

    def test_user_success(self):
        request_data = {'user': self.member['username']}
        self.help_test_success(self.task.id, request_data)
        self.assertEqual(Task.objects.get(id=self.task.id).user.username,
                         request_data.get('user'))

    def test_order_success(self):
        request_data = {'order': 10}
        self.help_test_success(self.task.id, request_data)
        self.assertEqual(Task.objects.get(id=self.task.id).order,
                         request_data.get('order'))

    def test_column_success(self):
        another_column = Column.objects.create(
            order=0,
            board=Board.objects.create(
                team=Team.objects.create()
            )
        )
        request_data = {'column': another_column.id}
        self.help_test_success(self.task.id, request_data)
        self.assertEqual(Task.objects.get(id=self.task.id).column.id,
                         request_data.get('column'))

    def test_assign_member_success(self):
        request_data = {'user': self.member['username']}
        self.help_test_success(self.task.id, request_data)
        self.assertEqual(Task.objects.get(id=self.task.id).user.username,
                         request_data.get('user'))

    def test_title_blank(self):
        response = self.client.patch(f'{self.endpoint}{self.task.id}',
                                     {'title': ''},
                                     HTTP_AUTH_USER=self.admin['username'],
                                     HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'title': [ErrorDetail(string='Task title cannot be blank.',
                                  code='blank')]
        })
        self.assertEqual(Task.objects.get(id=self.task.id).title,
                         self.task.title)

    def test_order_blank(self):
        response = self.client.patch(f'{self.endpoint}{self.task.id}',
                                     {'order': ''},
                                     HTTP_AUTH_USER=self.admin['username'],
                                     HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'order': [ErrorDetail(string='Task order must be a number.',
                                  code='invalid')]
        })
        self.assertEqual(Task.objects.get(id=self.task.id).order,
                         self.task.order)

    def test_column_blank(self):
        response = self.client.patch(f'{self.endpoint}{self.task.id}',
                                     {'column': ''},
                                     HTTP_AUTH_USER=self.admin['username'],
                                     HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'column': [ErrorDetail(string='Column ID must be a number.',
                                   code='invalid')]
        })
        self.assertEqual(Task.objects.get(id=self.task.id).column,
                         self.task.column)

    def test_column_not_found(self):
        response = self.client.patch(f'{self.endpoint}{self.task.id}',
                                     {'column': '123123'},
                                     HTTP_AUTH_USER=self.admin['username'],
                                     HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'task': {
                'column': [ErrorDetail(string='Task column does not exist.',
                                       code='does_not_exist')]
            }
        })
        self.assertEqual(Task.objects.get(id=self.task.id).column,
                         self.task.column)

    def test_user_not_found(self):
        response = self.client.patch(f'{self.endpoint}{self.task.id}',
                                     {'user': 'aasddas'},
                                     HTTP_AUTH_USER=self.admin['username'],
                                     HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'task': {
                'user': [ErrorDetail(string='User does not exist.',
                                     code='does_not_exist')]
            }
        })
        self.assertEqual(Task.objects.get(id=self.task.id).user,
                         self.task.user)

    def test_auth_token_empty(self):
        response = self.client.patch(f'{self.endpoint}{self.task.id}',
                                     {'title': 'New Title'},
                                     HTTP_AUTH_USER=self.admin['username'],
                                     HTTP_AUTH_TOKEN='')
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHENTICATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHENTICATION_ERROR.detail)

    def test_auth_token_invalid(self):
        response = self.client.patch(f'{self.endpoint}{self.task.id}',
                                     {'title': 'New Title'},
                                     HTTP_AUTH_USER=self.admin['username'],
                                     HTTP_AUTH_TOKEN='ADKFJ!FJ_012rjpiwajfosi')
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHENTICATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHENTICATION_ERROR.detail)

    def test_auth_user_blank(self):
        response = self.client.patch(f'{self.endpoint}{self.task.id}',
                                     {'title': 'New Title'},
                                     HTTP_AUTH_USER='',
                                     HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHENTICATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHENTICATION_ERROR.detail)

    def test_auth_user_invalid(self):
        response = self.client.patch(f'{self.endpoint}{self.task.id}',
                                     {'title': 'New Title'},
                                     HTTP_AUTH_USER='invalidio',
                                     HTTP_AUTH_TOKEN=self.admin['token'])
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHENTICATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHENTICATION_ERROR.detail)

    def test_not_authorized(self):
        response = self.client.patch(f'{self.endpoint}{self.task.id}',
                                     {'title': 'New Title'},
                                     HTTP_AUTH_USER=self.member['username'],
                                     HTTP_AUTH_TOKEN=self.member['token'])
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHORIZATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHORIZATION_ERROR.detail)

    def test_wrong_team(self):
        response = self.client.patch(
            f'{self.endpoint}{self.task.id}',
            {'title': 'New Title'},
            HTTP_AUTH_USER=self.wrong_admin['username'],
            HTTP_AUTH_TOKEN=self.wrong_admin['token']
        )
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHORIZATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHORIZATION_ERROR.detail)

    def test_assigned_member_failure(self):
        response = self.client.patch(
            f'{self.endpoint}{self.task.id}',
            {'title': 'New Title'},
            HTTP_AUTH_USER=self.assigned_member['username'],
            HTTP_AUTH_TOKEN=self.assigned_member['token']
        )
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHORIZATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHORIZATION_ERROR.detail)
