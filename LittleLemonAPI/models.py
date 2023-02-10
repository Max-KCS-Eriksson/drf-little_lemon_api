from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """
    A menu category.

    Searchable against title field.
    """

    slug = models.SlugField()
    title = models.CharField(max_length=225, db_index=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return f"({self.pk}) {self.title}"


class MenuItem(models.Model):
    """
    An item on the menu belonging to a category.

    Searchable against title, price, and featured fields.
    """

    title = models.CharField(max_length=225, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    class Meta:
        unique_together = ("title", "category")  # No duplicate items in same category.

    def __str__(self) -> str:
        return f"({self.category.pk}) {self.category.title}: ({self.pk}) {self.title}"


class Cart(models.Model):
    """Shopping cart of a user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    # Not needed as it is calculated in the serializer.
    # price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ("menuitem", "user")  # One entry per menuitem in a cart.

    def __str__(self) -> str:
        return f"({self.user.pk}) {self.user.username}: ({self.pk}) Cart"


class Order(models.Model):
    """
    An order made by a user.

    Searchable against status, and date fields.

    delivery_crew field allows null value.
    status field has a default value of 0 (boolean false).
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="delivery_crew", null=True
    )
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(db_index=True, auto_now_add=True)

    def __str__(self) -> str:
        return f"({self.user.pk}) {self.user.username}: ({self.pk}) Order"


class OrderItem(models.Model):
    """An item in an order."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ("order", "menuitem")  # One entry per menuitem in an order.

    def __str__(self) -> str:
        return f"({self.order.user.pk}) {self.order.user.username}: ({self.order.pk}) Order: ({self.menuitem.pk}) {self.menuitem.title}"
