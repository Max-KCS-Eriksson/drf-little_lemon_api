from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.http import Http404

from .models import MenuItem, Cart, Order, OrderItem
from .serializers import (
    MenuItemSerializer,
    UserSerializer,
    CartSerializer,
    OrderSerializer,
    OrderItemSerializer,
)


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


class DeliveryCrewView(generics.ListCreateAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.method == "GET":
            # Manager only for GET requests.
            return User.objects.filter(groups__name="Delivery crew")
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
        assign_user_to_group(user, "Delivery crew")
        return Response(status=status.HTTP_201_CREATED)


class RemoveDeliveryCrewView(generics.DestroyAPIView):
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
        remove_user_from_group(user, "Delivery crew")
        return Response(status=status.HTTP_200_OK)


class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)

    def post(self, request, *args, **kwargs):
        # Get current user, menuitem by title, and other POST request data.
        user = self.request.user
        request_data = self.request.POST
        menuitem = get_object_or_404(MenuItem, title=request_data.get("menuitem"))
        quantity = int(request_data.get("quantity"))
        unit_price = menuitem.price

        # Create cart and write to db.
        cart = Cart(
            user=user,
            menuitem=menuitem,
            quantity=quantity,
            unit_price=unit_price,
            # Price is calculated by the serializer.
            # price=quantity * unit_price,
        )
        cart.save()
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        # Delete all carts made by the current user.
        user = self.request.user
        carts = Cart.objects.filter(user=user)
        carts.delete()
        return Response(status=status.HTTP_200_OK)


class OrdersView(generics.ListCreateAPIView):
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        # Return all orders if user is a manager, and user created orders only if not.
        if is_manager(self.request):
            return OrderItem.objects.all()
        return OrderItem.objects.filter(order__user=self.request.user)

    def post(self, request, *args, **kwargs):
        # Get current user and all items in users cart.
        user = self.request.user
        cart_items = Cart.objects.filter(user=user)

        # Create new order and transfer items from cart.
        order_total = 0
        for cart_item in cart_items:
            order_total += cart_item.quantity * cart_item.unit_price
        new_order = Order(
            user=user,
            total=order_total,
        )
        # Write order and all order items to db, and delete cart items in one hit.
        order_items = []
        for cart_item in cart_items:
            order_items.append(
                OrderItem(
                    order=new_order,
                    menuitem=cart_item.menuitem,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    price=cart_item.quantity * cart_item.unit_price,
                )
            )
        new_order.save()
        OrderItem.objects.bulk_create(order_items)
        cart_items.delete()
        return Response(status=status.HTTP_201_CREATED)


class SingleOrderView(generics.ListAPIView):
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        # Ensure specified order exists, and user is owner of order or a manager.
        order = get_object_or_404(Order, pk=self.kwargs.get("pk"))
        if self.request.user != order.user and not is_manager(self.request):
            raise Http404

        # List all items of specified order.
        return OrderItem.objects.filter(order=order)
