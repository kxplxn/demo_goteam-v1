from rest_framework import serializers
from main.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'user': {
                'error_messages': {
                    'does_not_exist': 'User does not exist.'
                }
            },
            'title': {
                'error_messages': {
                    'blank': 'Title cannot be empty.',
                    'max_length': 'Title cannot be longer than 50 characters.'
                }
            },
            'column': {
                'error_messages': {
                    'does_not_exist': 'Task column does not exist.'
                }
            }
        }
