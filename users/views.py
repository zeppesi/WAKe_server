from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response


class RecordViewSet(viewsets.GenericViewSet):

    @action(methods=['GET'], detail=False, serializer_class=None)
    def random(self, request: Request):
        # return random selected contents
        return Response("hi")
