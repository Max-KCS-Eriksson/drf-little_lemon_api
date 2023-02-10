from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
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


def is_manager(user):
    """Checks if user making the request belongs to the manager role."""
    return user.groups.filter(name="Manager").exists()


def is_delivery_crew(user):
    """Checks if user making the request belongs to the delivery crew role."""
    return user.groups.filter(name="Delivery crew").exists()


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
    permission_classes = [AllowAny]
    ordering_fields = ["category__title", "title", "price", "featured"]
    search_fields = ["category__title", "title"]

    def post(self, request, *args, **kwargs):
        # Only allow request from managers.
        if not is_manager(self.request.user):
            return Response(
                {"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN
            )
        return super().post(request, *args, **kwargs)


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]

    def put(self, request, *args, **kwargs):
        # Only allow request from managers.
        if not is_manager(self.request.user):
            return Response(
                {"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN
            )
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        # Only allow request from managers.
        if not is_manager(self.request.user):
            return Response(
                {"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Only allow request from managers.
        if not is_manager(self.request.user):
            return Response(
                {"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN
            )
        menu_item = self.get_object()
        menu_item.delete()
        return Response(status=status.HTTP_200_OK)


class ManagersView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.method == "GET":
            # Manager only for GET requests.
            return User.objects.filter(groups__name="Manager")
        else:
            # All users for POST requests to allow assignment as Manager.
            return User.objects.all()

    def get(self, request, *args, **kwargs):
        # Only allow request from managers.
        if not is_manager(self.request.user):
            return Response(
                {"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN
            )
        return super().get(request, *args, **kwargs)

    def post(self, request):
        # Only allow request from managers.
        if not is_manager(self.request.user):
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
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        # Only allow request from managers.
        if not is_manager(self.request.user):
            return Response(
                {"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN
            )
        # Get user or 404, and remove from group.
        user = self.get_object()
        remove_user_from_group(user, "Manager")
        return Response(status=status.HTTP_200_OK)


class DeliveryCrewView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.method == "GET":
            # Manager only for GET requests.
            return User.objects.filter(groups__name="Delivery crew")
        else:
            # All users for POST requests to allow assignment as Manager.
            return User.objects.all()

    def get(self, request, *args, **kwargs):
        # Only allow request from managers.
        if not is_manager(self.request.user):
            return Response(
                {"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN
            )
        return super().get(request, *args, **kwargs)

    def post(self, request):
        # Only allow request from managers.
        if not is_manager(self.request.user):
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
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        # Only allow request from managers.
        if not is_manager(self.request.user):
            return Response(
                {"message": "You are not authorized"}, status.HTTP_403_FORBIDDEN
            )
        # Get user or 404, and remove from group.
        user = self.get_object()
        remove_user_from_group(user, "Delivery crew")
        return Response(status=status.HTTP_200_OK)


class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]
    ordering_fields = ["order__delivery_crew", "order__status", "order__date"]
    search_fields = [
        "menuitem__category__title",
        "menuitem__title",
        "order__user__username",
    ]

    def get_queryset(self):
        # Return all orders if user is a manager, and user created orders only if not.
        if is_manager(self.request.user):
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


class SingleOrderView(
    generics.ListAPIView, generics.UpdateAPIView, generics.DestroyAPIView
):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Query OrderItems of Order on GET requests.
        if self.request.method == "GET":
            # Ensure specified order exists.
            order = get_object_or_404(Order, pk=self.kwargs.get("pk"))
            # Ensure user is owner or a manager or in the delivery crew.
            if (
                self.request.user != order.user
                and not is_manager(self.request.user)
                and not is_delivery_crew(self.request.user)
            ):
                raise Http404

            # List all items of specified order.
            return OrderItem.objects.filter(order=order)

        # Query Order on PUT, PATCH, and DELETE.
        elif self.request.method in ["PUT", "PATCH", "DELETE"]:
            # Ensure user is a manager or in the delivery crew, and return Order.
            if not is_manager(self.request.user) or not is_delivery_crew(
                self.request.user
            ):
                return get_object_or_404(Order, pk=self.kwargs.get("pk"))

    def put(self, request, *args, **kwargs):
        # Allow only manager to completely update an order.
        if not is_manager(self.request.user):
            context = {"message": "You lack permission for this action"}
            return Response(context, status=status.HTTP_401_UNAUTHORIZED)

        # Get submitted data.
        post_data_user = self.request.POST.get("user")
        post_data_delivery_crew = self.request.POST.get("delivery_crew")
        post_data_status = self.request.POST.get("status")
        post_data_total = self.request.POST.get("total")
        post_data_date = self.request.POST.get("date")

        # Get specified user and delivery crew.
        updated_user = get_object_or_404(User, username=post_data_user)
        delivery_crew = get_object_or_404(User, username=post_data_delivery_crew)
        # Ensure delivery crew has correct role.
        if not is_delivery_crew(delivery_crew):
            return Response(
                {"message": "Invalid delivery crew assignment"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update specified order and write to db.
        order = self.get_queryset()
        order.user = updated_user
        order.delivery_crew = delivery_crew
        order.status = post_data_status
        order.total = post_data_total
        order.date = post_data_date
        order.save()
        return Response(status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        # Get submitted data.
        post_data_user = self.request.POST.get("user")
        post_data_delivery_crew = self.request.POST.get("delivery_crew")
        post_data_status = self.request.POST.get("status")
        post_data_total = self.request.POST.get("total")
        post_data_date = self.request.POST.get("date")

        # Check if request comes from a manager or delivery crew.
        if is_manager(self.request.user):
            # Managers can update everything.
            order = self.get_queryset()
            # Ensure order has a delivery crew assigned before changing status to True.
            if order.delivery_crew is None and post_data_status == "1":
                # Can't set order as delivered without a delivery crew assigned.
                message = "Invalid status assignment due to no delivery crew"
                return Response(
                    {"message": message},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Assign value if given in request data.
            if post_data_user:
                updated_user = get_object_or_404(User, username=post_data_user)
                order.user = updated_user
            if post_data_delivery_crew:
                delivery_crew = get_object_or_404(
                    User, username=post_data_delivery_crew
                )
                order.delivery_crew = delivery_crew
            if post_data_status:
                order.status = post_data_status
            if post_data_total:
                order.total = post_data_total
            if post_data_date:
                order.date = post_data_date
            order.save()
            return Response(status=status.HTTP_200_OK)

        elif is_delivery_crew(self.request.user):
            order = self.get_queryset()
            # Ensure a request comes from assigned delivery crew.
            if self.request.user != order.delivery_crew:
                return Response(
                    {"message": "Not assigned to this order"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            # Delivery crew can ONLY update status field.
            if (
                post_data_user
                or post_data_delivery_crew
                or post_data_total
                or post_data_date
            ):
                return Response(
                    {"message": "Delivery crew can only update status"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            if post_data_status:
                # Update status of specified order and write to db.
                order.status = post_data_status
                order.save()
                return Response(status=status.HTTP_200_OK)
            return Response(
                {"message": "No update to status was given"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, *args, **kwargs):
        # Allow only manager to delete an order.
        if not is_manager(self.request.user):
            context = {"message": "You lack permission for this action"}
            return Response(context, status=status.HTTP_401_UNAUTHORIZED)
        order = self.get_queryset()
        order.delete()
        return Response(status=status.HTTP_200_OK)
