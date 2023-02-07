from django.urls import path

from . import views

app_name = "LittleLemonAPI"
urlpatterns = [
    path("menu-items", views.MenuItemsView.as_view()),
    path("menu-items/<int:pk>", views.SingleMenuItemView.as_view()),
]
