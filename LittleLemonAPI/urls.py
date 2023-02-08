from django.urls import path

from . import views

app_name = "LittleLemonAPI"
urlpatterns = [
    # Menu-items endpoints.
    path("menu-items", views.MenuItemsView.as_view()),
    path("menu-items/<int:pk>", views.SingleMenuItemView.as_view()),
    # User role management endpoint.
    path("groups/manager/users", views.ManagersView.as_view()),
    path("groups/manager/users/<int:pk>", views.RemoveManagerView.as_view()),
]
