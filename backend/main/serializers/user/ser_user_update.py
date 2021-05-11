from rest_framework import serializers
import status

from main.serializers.user.ser_user import UserSerializer
from main.validation.val_auth import authenticate, authorize
from main.validation.val_custom import CustomAPIException
from main.models import User, Board


class UpdateUserSerializer(UserSerializer):
    """
    Used only for adding/removing a user to/from a board
    """
    board_id = serializers.IntegerField(error_messages={
        'blank': 'Board ID cannot be blank.',
        'null': 'Board ID cannot be null.',
        'invalid': 'Board ID must be a number.'
    })
    is_active = serializers.BooleanField(error_messages={
        'blank': 'Is Active cannot be blank.',
        'null': 'Is Active cannot be null.',
        'invalid': 'Is Active must be a boolean.'
    })
    auth_user = serializers.CharField(allow_blank=True)
    auth_token = serializers.CharField(allow_blank=True)

    class Meta:
        model = UserSerializer.Meta.model
        fields = 'username', 'board_id', 'is_active', 'auth_user', \
                 'auth_token',

    def validate(self, attrs):
        authenticated_user = authenticate(attrs.pop('auth_user'),
                                          attrs.pop('auth_token'))

        try:
            board = Board.objects.prefetch_related('user', 'team__user_set') \
                                 .get(id=attrs.get('board_id'))
        except Board.DoesNotExist:
            raise CustomAPIException('board_id',
                                     'Board not found.',
                                     status.HTTP_404_NOT_FOUND)

        try:
            user = board.team.user_set.get(username=attrs.get('username'))
        except User.DoesNotExist:
            raise CustomAPIException('username',
                                     'User not found.',
                                     status.HTTP_404_NOT_FOUND)

        authorize(authenticated_user, user.team_id)

        self.instance = {'user': user,
                         'board': board,
                         'is_active': attrs.get('is_active')}

        return attrs

    def update(self, instance, validated_data):
        board = instance.get('board')
        user = instance.get('user')
        if instance.get('is_active'):
            board.user.add(user)
        else:
            board.user.remove(user)
        return instance

    def to_representation(self, instance):
        user = instance.get('user')
        board = instance.get('board')
        action = 'added' if instance.get('is_active') else 'removed'
        return {
            'msg': f'{user.username} is {action} from {board.name}.'
        }
