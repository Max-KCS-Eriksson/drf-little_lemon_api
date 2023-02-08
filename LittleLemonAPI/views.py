from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from .models import MenuItem
from .serializers import MenuItemSerializer, UserSerializer


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


class ManagersView(generics.ListCreateAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.method == "GET":
            # Manager only for GET requests.
            return User.objects.filter(groups__name="Manager")
        else:
            # All users for POST requests to allow assignment as Manager.
            return User.objects.all()

    def get(self, request, *args, **kwargs):
        # Only allow request from managers.
        if not is_manager(request):
            return Response(
                {"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN
            )
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Only allow request from managers.
        if not is_manager(request):
            return Response(
                {"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN
            )

        # Get user or 404.
        user = get_object_or_404(User, username=request.POST.get("username"))

        # Assign user to group.
        manager_group = Group.objects.get(name="Manager")
        manager_group.user_set.add(user)
        return Response(status=status.HTTP_201_CREATED)
        # return super().post(request, *args, **kwargs)
