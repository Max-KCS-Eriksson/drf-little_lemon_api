from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Category, MenuItem, Cart, Order, OrderItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "title"]


class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField()

    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "featured", "category", "category_id"]
        depth = 1


class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    user_id = serializers.IntegerField()
    menuitem_id = serializers.IntegerField()
    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "user_id",
            "menuitem",
            "menuitem_id",
            "quantity",
            "unit_price",
            "total_price",
        ]
        depth = 1

    def get_total_price(self, cart_item: Cart):
        return cart_item.unit_price * cart_item.quantity


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    user_id = serializers.IntegerField()
    delivery_crew_id = serializers.IntegerField()

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "user_id",
            "delivery_crew",
            "delivery_crew_id",
            "status",
            "total",
            "date",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer()
    order_id = serializers.IntegerField()
    menuitem_id = serializers.IntegerField()
    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "order_id",
            "menuitem",
            "menuitem_id",
            "quantity",
            "unit_price",
            "total_price",
        ]
        depth = 2

    def get_total_price(self, order_item: OrderItem):
        return order_item.price * order_item.quantity
