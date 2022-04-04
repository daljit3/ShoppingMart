from django.core.exceptions import PermissionDenied
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.db.models import Count

from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render

from django.urls import reverse_lazy

from django.views import View
from django.views.generic import ListView, UpdateView

# Load models
from .models import ShoppingList, ShoppingListItem

# Load forms
from .forms import SignUpForm, ShoppingListForm, ShoppingListItemCategoryForm, ShoppingListItemForm, CompleteAListItemForm, ArchiveListForm

import json
# Views


def home(request):
    return render(request, 'home.html')


class SignUpView(View):
    form_class = SignUpForm
    initial = {}
    template_name = 'sign_up.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # process form cleaned data
            email = form.cleaned_data.get('email').lower()
            user = form.save(commit=False)
            user.username = email
            user.save()

            # Send welcome email
            # .............
            # Log in the user
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            return redirect('/')

        return render(request, self.template_name, {'form': form})


class DashboardListView(ListView):
    """ Once a user log in, they can view their shopping lists """
    model = ShoppingList
    form_class = ShoppingListForm
    initial = {}
    template_name = "dashboard.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        # get user's shopping lists along with their total number of items in that list.
        user_lists = ShoppingList.objects.filter(
            user=self.request.user).annotate(num_of_items=Count('shoppinglistitem'))

        return render(request, self.template_name, {'form': form, 'user_lists': user_lists})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # process form's cleaned data
            new_list = form.save(commit=False)
            new_list.user = self.request.user
            new_list.save()

            #created = new_list.id
            return redirect('dashboard')

        return render(request, self.template_name, {'form': form})


class ShoppingListItemsView(View):
    model = ShoppingListItem
    form_class = ShoppingListItemForm
    initial = {}
    template_name = "shopping_list_items.html"

    def get(self, request, *args, **kwargs):
        list_id = kwargs['list_id']

        shopping_list = ShoppingList.objects.get(pk=list_id)

        # Check if user is allowed to view/modify requested list
        if self.request.user != shopping_list.user:
            messages.add_message(
                request, messages.WARNING, 'Error: You do not have enough permissions to access that resource.')
            #raise PermissionDenied
            return redirect('dashboard')

        # try:
        #     shopping_list = ShoppingList.objects.filter(
        #         user=self.request.user).get(pk=list_id)
        # except ShoppingList.DoesNotExist:
        #     messages.add_message(request, messages.WARNING,
        #                          'Requested list could not be found.')
        #     return redirect('dashboard')

        # User can add a new item / new category from this page too
        form_list_item = self.form_class(
            initial=self.initial, user=self.request.user)
        form_category = ShoppingListItemCategoryForm()

        # Get list of items in the requested list
        list_items = ShoppingListItem.objects.select_related(
            'category').prefetch_related('category').filter(shopping_list=list_id)

        return render(request, self.template_name, {'form_list_item': form_list_item, 'form_category': form_category, 'shopping_list': shopping_list, 'list_items': list_items})

    def post(self, request, *args, **kwargs):
        list_id = kwargs['list_id']
        form_list_item = self.form_class(request.POST, user=self.request.user)

        if form_list_item.is_valid():
            # process form cleaned data
            new_item = form_list_item.save(commit=False)
            new_item.shopping_list = ShoppingList.objects.filter(
                user=self.request.user).get(pk=list_id)
            new_item.user = self.request.user
            new_item.save()
            #created = new_item.id
            messages.add_message(request, messages.SUCCESS,
                                 'Item added successfully.')
            return redirect('list_items', list_id)

        return render(request, self.template_name, {'form_list_item': form_list_item})


class ShoppingListItemEditView(UpdateView):
    model = ShoppingListItem
    form_class = ShoppingListItemForm
    template_name = "shopping_item_edit.html"
    # success_url = reverse_lazy('list_items', kwargs={'list_id':})

    def get_success_url(self, **kwargs):
        return reverse_lazy('list_items', kwargs={'list_id': self.object.shopping_list.id})

    """ If user don't own this record, just show 404 """

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404
        return obj

    # Sending user object to the form
    def get_form_kwargs(self):
        kwargs = super(ShoppingListItemEditView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

# http://127.0.0.1:8000/edit_item/18/6


@login_required
def mark_list_as_archived(request, list_id):
    """ Allow user to mark only their own list to be archived or un-archived """
    if request.method == 'POST':
        form = ArchiveListForm(request.POST)
        response_data = {}
        if form.is_valid():
            shoppinglist = ShoppingList.objects.filter(
                user=request.user).get(pk=list_id)
            shoppinglist.archived = form.cleaned_data.get("archived")
            shoppinglist.save()

            response_data['success'] = True
            response_data['message'] = 'List updated successful!'
        else:
            response_data['success'] = True
            response_data['message'] = 'List could not be updated.'

        return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
def mark_list_item_completed(request, list_id, item_id):
    """ Allow user to mark only their own item to be completed or un-completed """
    if request.method == 'POST':
        form = CompleteAListItemForm(request.POST)
        response_data = {}
        if form.is_valid():
            item = ShoppingListItem.objects.filter(
                user=request.user).get(pk=item_id)
            item.completed = form.cleaned_data.get("completed")
            item.save()

            response_data['success'] = True
            response_data['message'] = 'Item updated successful!'
        else:
            response_data['success'] = True
            response_data['message'] = 'Item could not be updated.'

        return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
def delete_list_item(request, item_id):
    """ Allow user to delete their own items only """
    if request.method == 'POST':
        item = ShoppingListItem.objects.filter(
            user=request.user).get(pk=item_id)
        response_data = {}
        if item:
            item.delete()
            response_data['success'] = True
            response_data['message'] = 'Item deleted successful!'
        else:
            response_data['success'] = False
            response_data['message'] = 'Item could not be deleted!'

        return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
def save_list_item_category(request, list_id):
    """ list_id is only required to redirect back to the same list where user added the category from ... """
    if request.method == 'POST':
        form = ShoppingListItemCategoryForm(request.POST)
        if form.is_valid():

            new_category = form.save(commit=False)
            new_category.user = request.user
            new_category.save()

            return redirect('list_items', list_id)
