from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from ..models import Subtask, Task, Column, Board, Team, User
from main.helpers.user_helper import UserHelper
from main.helpers.auth_helper import AuthHelper


class UpdateSubtaskTests(APITestCase):
    endpoint = '/subtasks/?id='

    def setUp(self):
        team = Team.objects.create()

        user_helper = UserHelper(team)
        self.member = user_helper.create_user()
        self.admin = user_helper.create_user(is_admin=True)
        self.assigned_member = user_helper.create_user()

        wrong_user_helper = UserHelper(Team.objects.create())
        self.wrong_admin = wrong_user_helper.create_user(is_admin=True)

        self.subtask = Subtask.objects.create(
            title='Some Task Title',
            order=0,
            task=Task.objects.create(
                title="Some Subtask Title",
                order=0,
                user=User.objects.get(
                    username=self.assigned_member['username']
                ),
                column=Column.objects.create(
                    order=0,
                    board=Board.objects.create(team=team)
                )
            )
        )

    def help_test_success(self, user, subtask_id, request_data):
        response = self.client.patch(f'{self.endpoint}{subtask_id}',
                                     request_data,
                                     HTTP_AUTH_USER=user['username'],
                                     HTTP_AUTH_TOKEN=user['token'],
                                     format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'msg': 'Subtask update successful.',
                                         'id': self.subtask.id})
        return Subtask.objects.get(id=self.subtask.id)

    def help_test_failure(self):
        subtask = Subtask.objects.get(id=self.subtask.id)
        self.assertEqual(subtask.title, self.subtask.title)
        self.assertEqual(subtask.done, self.subtask.done)

    def test_title_success(self):
        request_data = {'title': 'New Task Title'}
        subtask = self.help_test_success(
            self.admin, self.subtask.id, request_data
        )
        self.assertEqual(subtask.title, request_data.get('title'))

    def test_assigned_member_success(self):
        request_data = {'title': 'New Task Title'}
        subtask = self.help_test_success(
            self.assigned_member, self.subtask.id, request_data
        )
        self.assertEqual(subtask.title, request_data.get('title'))

    def test_done_success(self):
        request_data = {'done': True}
        subtask = self.help_test_success(
            self.admin, self.subtask.id, request_data
        )
        self.assertEqual(subtask.done, request_data.get('done'))

    def test_order_success(self):
        request_data = {'order': 10}
        subtask = self.help_test_success(
            self.admin, self.subtask.id, request_data
        )
        self.assertEqual(subtask.order, request_data.get('order'))

    def test_id_blank(self):
        request_data = {'title': 'New task title.'}
        response = self.client.patch(self.endpoint,
                                     request_data,
                                     HTTP_AUTH_USER=self.admin['username'],
                                     HTTP_AUTH_TOKEN=self.admin['token'],
                                     format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'subtask': [ErrorDetail(string='Subtask ID cannot be null.',
                                    code='null')]
        })
        self.help_test_failure()

    def test_data_blank(self):
        response = self.client.patch(f'{self.endpoint}{self.subtask.id}',
                                     None,
                                     HTTP_AUTH_USER=self.admin['username'],
                                     HTTP_AUTH_TOKEN=self.admin['token'],
                                     format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'data': [ErrorDetail(string='Subtask data cannot be empty.',
                                 code='empty')]
        })
        self.help_test_failure()

    def test_title_blank(self):
        response = self.client.patch(f'{self.endpoint}{self.subtask.id}',
                                     {'title': ''},
                                     HTTP_AUTH_USER=self.admin['username'],
                                     HTTP_AUTH_TOKEN=self.admin['token'],
                                     format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'title': ErrorDetail(string='Title cannot be empty.',
                                 code='blank')
        })
        self.help_test_failure()

    def test_done_blank(self):
        request_data = {'done': ''}
        response = self.client.patch(f'{self.endpoint}{self.subtask.id}',
                                     request_data,
                                     HTTP_AUTH_USER=self.admin['username'],
                                     HTTP_AUTH_TOKEN=self.admin['token'],
                                     format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'done': ErrorDetail(string='Done cannot be empty.',
                                code='blank')
        })
        self.help_test_failure()

    def test_order_blank(self):
        response = self.client.patch(f'{self.endpoint}{self.subtask.id}',
                                     {'order': ''},
                                     HTTP_AUTH_USER=self.admin['username'],
                                     HTTP_AUTH_TOKEN=self.admin['token'],
                                     format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'order': ErrorDetail(string='Order cannot be empty.',
                                 code='blank')
        })
        self.help_test_failure()

    def test_auth_token_empty(self):
        response = self.client.patch(f'{self.endpoint}{self.subtask.id}',
                                     {'title': 'New Task Title'},
                                     HTTP_AUTH_USER=self.admin['username'],
                                     HTTP_AUTH_TOKEN='',
                                     format='json')
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHENTICATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHENTICATION_ERROR.detail)

    def test_auth_token_invalid(self):
        response = self.client.patch(f'{self.endpoint}{self.subtask.id}',
                                     {'title': 'New Task Title'},
                                     HTTP_AUTH_USER=self.admin['username'],
                                     HTTP_AUTH_TOKEN='ASDKFJ!FJ_012rjpiwajfos',
                                     format='json')
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHENTICATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHENTICATION_ERROR.detail)

    def test_auth_user_blank(self):
        response = self.client.patch(f'{self.endpoint}{self.subtask.id}',
                                     {'title': 'New Task Title'},
                                     HTTP_AUTH_USER='',
                                     HTTP_AUTH_TOKEN=self.admin['token'],
                                     format='json')
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHENTICATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHENTICATION_ERROR.detail)

    def test_auth_user_invalid(self):
        response = self.client.patch(f'{self.endpoint}{self.subtask.id}',
                                     {'title': 'New Task Title'},
                                     HTTP_AUTH_USER='invalidio',
                                     HTTP_AUTH_TOKEN=self.admin['token'],
                                     format='json')
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHENTICATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHENTICATION_ERROR.detail)

    def test_wrong_team(self):
        response = self.client.patch(
            f'{self.endpoint}{self.subtask.id}',
            {'title': 'New Task Title'},
            HTTP_AUTH_USER=self.wrong_admin['username'],
            HTTP_AUTH_TOKEN=self.wrong_admin['token'],
            format='json'
        )
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHORIZATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHORIZATION_ERROR.detail)

    def test_unauthorized(self):
        response = self.client.patch(f'{self.endpoint}{self.subtask.id}',
                                     {'title': 'New Task Title'},
                                     HTTP_AUTH_USER=self.member['username'],
                                     HTTP_AUTH_TOKEN=self.member['token'],
                                     format='json')
        self.assertEqual(response.status_code,
                         AuthHelper.AUTHORIZATION_ERROR.status_code)
        self.assertEqual(response.data,
                         AuthHelper.AUTHORIZATION_ERROR.detail)
