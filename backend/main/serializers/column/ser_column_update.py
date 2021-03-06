from rest_framework import serializers
import status

from .ser_column import ColumnSerializer
from ..task.ser_task import TaskSerializer
from ...models import Column, Task
from main.helpers.auth_helper import AuthHelper
from main.helpers.custom_api_exception import CustomAPIException


class UpdateColumnSerializer(ColumnSerializer):
    column = serializers.PrimaryKeyRelatedField(
        queryset=Column.objects.select_related('board').all(),
        error_messages={
            'blank': 'Column ID cannot be blank.',
            'null': 'Column ID cannot be null.',
            'invalid': 'Column ID must be a number.'
        },
    )
    tasks = serializers.ListField(allow_empty=True)
    auth_user = serializers.CharField(allow_blank=True)
    auth_token = serializers.CharField(allow_blank=True)

    class Meta:
        model = ColumnSerializer.Meta.model
        fields = 'column', 'tasks', 'auth_user', 'auth_token'

    def validate(self, attrs):
        user = AuthHelper.authenticate(attrs.pop('auth_user'),
                                       attrs.pop('auth_token'))
        attrs['user'] = user

        column = attrs.pop('column')
        if user.team_id != column.board.team_id:
            raise AuthHelper.AUTHORIZATION_ERROR

        self.instance = column
        return attrs

    def update(self, instance, validated_data):
        board_tasks = Task.objects.filter(column__board_id=instance.board_id)
        for task in validated_data.get('tasks'):
            try:
                task_id = task.pop('id')
            except KeyError:
                raise CustomAPIException('task.id',
                                         'Task ID cannot be empty.',
                                         status.HTTP_400_BAD_REQUEST)

            existing_task = board_tasks.get(id=task_id)

            user = validated_data.get('user')
            if not user.is_admin \
                    and task.get('user') != user.username \
                    and instance.id != existing_task.column_id:
                raise AuthHelper.AUTHORIZATION_ERROR

            serializer = TaskSerializer(existing_task,
                                        data={**task, 'column': instance.id},
                                        partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                raise serializer.errors

        return instance

    def to_representation(self, instance):
        return {
            'msg': 'Column and all its tasks updated successfully.',
            'id': instance.id,
        }
