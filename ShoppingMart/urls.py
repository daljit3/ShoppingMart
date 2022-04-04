"""ShoppingMart URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views  # For authentication
from ShoppingApp import views

urlpatterns = [
    path('bmx-admin/', admin.site.urls),
    path('', views.home, name='home'),

    path('sign-in/', auth_views.LoginView.as_view(template_name="sign_in.html")),
    path('sign-out/', auth_views.LogoutView.as_view(next_page="/")),
    path('sign-up/', views.SignUpView.as_view(), name='signup'),

    # Shopping list
    path('dashboard/', login_required(views.DashboardListView.as_view()),
         name='dashboard'),
    path('archive_list/<int:list_id>',
         views.mark_list_as_archived, name='archive_list'),

    # Shopping List items
    # @Todo - to refactor and organise views into their own folders - shopping_list_items/urls.py
    path('items/<int:list_id>',
         login_required(views.ShoppingListItemsView.as_view()), name='list_items'),
    path('edit_item/<int:list_id>/<int:pk>',
         views.ShoppingListItemEditView.as_view(), name='edit_item'),
    path('complete_item/<int:list_id>/<int:item_id>',
         views.mark_list_item_completed, name='complete_item'),
    path('delete_item/<int:item_id>',
         views.delete_list_item, name='delete_item'),

    # Item Category
    # @Todo - to refactor and organise views into their own folders - shopping_list_item_category/urls.py
    path('categories/', login_required(views.CategoriesListView.as_view()),
         name='categories'),
    path('edit_category/<int:pk>', login_required(
        views.ShoppingListItemCategoryEditView.as_view()), name='edit_category'),
    path('delete_category/<int:pk>',
         login_required(views.CategoryDeleteView.as_view()), name='delete_category'),
    path('save_item_category/<int:list_id>',
         views.save_list_item_category, name='save_item_category'),
]
