from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from ..models import User, Board, Team
from ..util import new_admin


class PostUsersTests(APITestCase):
    def setUp(self):
        team = Team.objects.create()
        self.admin = new_admin(team)
        self.user = User.objects.create(
            username='Some User',
            password=b'$2b$12$DKVJHUAQNZqIvoi.OMN6v.x1ZhscKhbzSxpOBMykHgTIMeeJ'
                     b'pC6m',
            is_admin=False,
            team=team
        )
        self.board = Board.objects.create(name='Some Board', team=team)
        self.board.user.add(self.user)
        self.username = self.user.username
        self.token = '$2b$12$WLmxQnf9kbDoW/8jA6kfIO9TfchCiGphBpckS2oy755wtdT' \
                     'aIQsoq'

    def postUser(self, user_data, auth_user, auth_token):
        return self.client.post(f'/users/',
                                user_data,
                                format='json',
                                HTTP_AUTH_USER=auth_user,
                                HTTP_AUTH_TOKEN=auth_token)

    def test_success(self):
        response = self.postUser({
            'username': self.user.username,
            'board_id': self.board.id,
            'is_active': False
        }, self.admin['username'], self.admin['token'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'msg': f'{self.user.username} is removed from {self.board.name}.'
        })
        self.assertEqual(
            len(self.board.user.filter(username=self.user.username)),
            0
        )

    def test_username_blank(self):
        response = self.postUser({
            'username': '',
            'board_id': self.board.id,
            'is_active': False
        }, self.admin['username'], self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'username': ErrorDetail(string='Username cannot be empty.',
                                    code='blank')
        })

    def test_user_not_found(self):
        response = self.postUser({
            'username': 'adksjhdsak',
            'board_id': self.board.id,
            'is_active': False
        }, self.admin['username'], self.admin['token'])
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {
            'username': ErrorDetail(string='User not found.',
                                    code='not_found')
        })

    def test_board_id_blank(self):
        response = self.postUser({
            'username': self.user.username,
            'board_id': '',
            'is_active': False
        }, self.admin['username'], self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'board_id': ErrorDetail(string='Board ID cannot be empty.',
                                    code='blank')
        })

    def test_board_id_invalid(self):
        response = self.postUser({
            'username': self.user.username,
            'board_id': 'sakdjas',
            'is_active': False
        }, self.admin['username'], self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'board_id': ErrorDetail(string='Board ID must be a number.',
                                    code='invalid')
        })

    def test_board_not_found(self):
        response = self.postUser({
            'username': self.user.username,
            'board_id': '12301024',
            'is_active': False
        }, self.admin['username'], self.admin['token'])
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {
            'board_id': ErrorDetail(string='Board not found.',
                                    code='not_found')
        })

    def test_is_active_blank(self):
        response = self.postUser({
            'username': self.user.username,
            'board_id': self.board.id,
            'is_active': ''
        }, self.admin['username'], self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'is_active': ErrorDetail(string='Is Active cannot be empty.',
                                     code='blank')
        })

    def test_is_active_invalid(self):
        response = self.postUser({
            'username': self.user.username,
            'board_id': self.board.id,
            'is_active': 'sdaa'
        }, self.admin['username'], self.admin['token'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            'is_active': ErrorDetail(string='Is Valid must be a boolean.',
                                     code='invalid')
        })
