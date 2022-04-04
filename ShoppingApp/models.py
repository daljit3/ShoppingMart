from pyexpat import model
from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields.related import ForeignKey
from django.utils import timezone

# Models here.


class ShoppingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=False)
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class ShoppingListItemCategory(models.Model):
    name = models.CharField(max_length=200, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ShoppingListItem(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)  # models.TextField(null=False)
    quantity = models.IntegerField(null=False, default=1)
    completed = models.BooleanField(default=False)
    #category = models.CharField(max_length=200, blank=True, default='')
    category = models.ForeignKey(
        ShoppingListItemCategory, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    # def category_as_list(self):
    #     return self.category.split(',')
