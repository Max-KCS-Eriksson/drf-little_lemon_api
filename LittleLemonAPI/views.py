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


def assign_user_to_group(user: User, group_name: str):
    """Assign instance of a user to a group specified by name as a string."""
    manager_group = get_object_or_404(Group, name=group_name)
    manager_group.user_set.add(user)


def remove_user_from_group(user: User, group_name: str):
    """Remove instance of a user from a group specified by name as a string."""
    manager_group = get_object_or_404(Group, name=group_name)
    user.groups.remove(manager_group)


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

    def delete(self, request, *args, **kwargs):
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

    def post(self, request):
        # Only allow request from managers.
        if not is_manager(request):
            return Response(
                {"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN
            )

        # Get user or 404, and assign to group.
        user = get_object_or_404(User, username=request.POST.get("username"))
        assign_user_to_group(user, "Manager")
        return Response(status=status.HTTP_201_CREATED)


class RemoveManagerView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def delete(self, request, *args, **kwargs):
        # Only allow request from managers.
        if not is_manager(request):
            return Response(
                {"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN
            )
        # Get user or 404, and remove from group.
        user = self.get_object()
        remove_user_from_group(user, "Manager")
        return Response(status=status.HTTP_200_OK)
