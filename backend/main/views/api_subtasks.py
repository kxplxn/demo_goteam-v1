from rest_framework.views import APIView
from rest_framework.response import Response
import status

from main.serializers.subtask.ser_subtask_update import UpdateSubtaskSerializer


class SubtasksApiView(APIView):
    @staticmethod
    def patch(request):
        serializer = UpdateSubtaskSerializer(data={
            'subtask': request.query_params.get('id'),
            'data': request.data,
            'auth_user': request.META.get('HTTP_AUTH_USER'),
            'auth_token': request.META.get('HTTP_AUTH_TOKEN')
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
