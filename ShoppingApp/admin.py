from django.contrib import admin

# Register your models here.
from .models import *

#


class CustomDashboardShoppingList(admin.ModelAdmin):
    list_display = ('name', 'user')
    list_filter = ('user',)


class CustomDashboardShoppingListItem(admin.ModelAdmin):
    list_display = ('name', 'shopping_list', 'user')
    list_filter = ('user',)


class CustomDashboardShoppingListItemCategory(admin.ModelAdmin):
    list_display = ('name', 'user')
    list_filter = ('user',)


# Register model and provide list of columns to be displayed and for filtering
admin.site.register(ShoppingList, CustomDashboardShoppingList)
admin.site.register(ShoppingListItem, CustomDashboardShoppingListItem)
admin.site.register(ShoppingListItemCategory,
                    CustomDashboardShoppingListItemCategory)
