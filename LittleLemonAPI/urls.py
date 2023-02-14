from django.urls import path

from . import views

app_name = "LittleLemonAPI"
urlpatterns = [
    # Menu-items endpoints.
    path("categories", views.CategoryView.as_view()),
    path("menu-items", views.MenuItemsView.as_view()),
    path("menu-items/<int:pk>", views.SingleMenuItemView.as_view()),
    # User role management endpoints.
    path("groups/manager/users", views.ManagersView.as_view()),
    path("groups/manager/users/<int:pk>", views.RemoveManagerView.as_view()),
    path("groups/delivery-crew/users", views.DeliveryCrewView.as_view()),
    path("groups/delivery-crew/users/<int:pk>", views.RemoveDeliveryCrewView.as_view()),
    # Cart and Order management endpoints.
    path("cart/menu-items", views.CartView.as_view()),
    path("cart/orders", views.OrdersView.as_view()),
    path("orders", views.OrdersView.as_view()),
    path("cart/orders/<int:pk>", views.SingleOrderView.as_view()),
    path("orders/<int:pk>", views.SingleOrderView.as_view()),
]
