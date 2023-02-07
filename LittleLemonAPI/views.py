from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from .models import MenuItem
from .serializers import MenuItemSerializer


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def post(self, request, *args, **kwargs):
        if request.user.groups.filter(name="Manager").exists():
            return super().post(request, *args, **kwargs)
        else:
            return Response(
                {"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN
            )
