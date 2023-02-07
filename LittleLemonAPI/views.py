from rest_framework import generics, status
from rest_framework.response import Response

from .models import MenuItem
from .serializers import MenuItemSerializer


def is_manager(request):
    """Checks if user making the request belongs to the manager role."""
    return request.user.groups.filter(name="Manager").exists()


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def post(self, request, *args, **kwargs):
        # Only allow request from managers.
        if not is_manager(request):
            return Response(
                {"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN
            )
        return super().post(request, *args, **kwargs)


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def put(self, request, *args, **kwargs):
        # Only allow request from managers.
        if not is_manager(request):
            return Response(
                {"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN
            )
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        # Only allow request from managers.
        if not is_manager(request):
            return Response(
                {"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)

    def delete(self, request):
        # Only allow request from managers.
        if not is_manager(request):
            return Response(
                {"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN
            )
        menu_item = self.get_object()
        menu_item.delete()
        return Response(status=status.HTTP_200_OK)
