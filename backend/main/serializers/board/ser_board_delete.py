from rest_framework import serializers
import status

from main.serializers.board.ser_board import BoardSerializer
from main.validation.val_auth import authenticate, authorization_error, \
    authorize
from main.validation.val_custom import CustomAPIException
from main.models import Board


class DeleteBoardSerializer(serializers.ModelSerializer):
    auth_user = serializers.CharField(allow_blank=True)
    auth_token = serializers.CharField(allow_blank=True)
    id = serializers.IntegerField(error_messages={
        'null': 'Board ID cannot be null.',
        'invalid': 'Board ID must be a number.'
    })

    class Meta:
        model = BoardSerializer.Meta.model
        fields = 'id', 'auth_user', 'auth_token',

    def validate(self, attrs):
        user = authenticate(attrs.get('auth_user'), attrs.get('auth_token'))

        try:
            board = Board.objects.get(id=attrs.get('id'))
        except Board.DoesNotExist:
            raise CustomAPIException('board_id',
                                     'Board not found.',
                                     status.HTTP_404_NOT_FOUND)

        authorize(user, board.team_id)

        return board

    def delete(self):
        self.instance = {'id': self.validated_data.id}
        return self.validated_data.delete()

    def to_representation(self, instance):
        return {
            'msg': 'Board deleted successfully.',
            'id': instance.get('id'),
        }


