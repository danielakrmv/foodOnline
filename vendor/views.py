from django.shortcuts import render, get_object_or_404, redirect
from .forms import VendorForm, OpeningHourForm
from accounts.forms import UserProfileForm

from accounts.models import UserProfile
from .models import Vendor, OpeningHour
from django.contrib import messages

from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor
from menu.models import Category, FoodItem
from menu.forms import CategoryForm, FoodItemForm
from orders.models import Order, OrderedFood
# from django.template.defaultfilters import slugify
from django.utils.text import slugify
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError
import json

# Create your views here.

def get_vendor(request):
    """
    Retrieve the Vendor object associated with the logged-in user.
    
    Args:
        request (HttpRequest): The HTTP request object.
    
    Returns:
        Vendor: The Vendor object associated with the user.
    """
    return Vendor.objects.get(user=request.user)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):
    """
    Handle vendor profile view and updates.

    This view allows vendors to view and update their profile information. It handles 
    both GET and POST requests to display the profile form and save updates respectively.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered template for vendor profile.
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Settings updated.')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }
    return render(request, 'vendor/vprofile.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    """
    Display the menu builder view for vendors.

    This view shows the categories of food items for the logged-in vendor and allows them 
    to manage their menu.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered template for menu builder.
    """
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories': categories,
    }
    return render(request, 'vendor/menu_builder.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk=None):
    """
    Display food items by category for a vendor.

    This view shows the food items under a specific category for the logged-in vendor.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the category.

    Returns:
        HttpResponse: The rendered template for food items by category.
    """
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {
        'fooditems': fooditems,
        'category': category,
    }
    return render(request, 'vendor/fooditems_by_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    """
    Handle adding a new category for a vendor.

    This view allows vendors to add new categories to their menu. It handles both GET and 
    POST requests to display the category form and save the new category respectively.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered template for adding a category.
    """
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            # category = form.save(commit=False)
            vendor = get_vendor(request)

            # Check if the category already exists for this vendor
            if Category.objects.filter(category_name=category_name, vendor=vendor).exists():
                form.add_error('category_name', 'Category with this name already exists for this vendor.')
            else:
                category = form.save(commit=False)
                category.vendor = get_vendor(request)
                category.save() # here the category id will be generated
                category.slug = slugify(category_name, allow_unicode=True)+'-'+str(category.id) # chicken-15
                category.save()
                messages.success(request, 'Категорията е добавена успешно!')
                return redirect('menu_builder')
        else:
            print(form.errors)

    else:
        form = CategoryForm()
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    """
    Handle editing an existing category for a vendor.

    This view allows vendors to edit existing categories in their menu. It handles both 
    GET and POST requests to display the category form and save the updates respectively.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the category.

    Returns:
        HttpResponse: The rendered template for editing a category.
    """
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)

        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name, allow_unicode=True)
            form.save()
            messages.success(request, 'Категорията е обновена успешно!')
            return redirect('menu_builder')
    else:
        form = CategoryForm(instance=category)
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'vendor/edit_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    """
    Handle deleting a category for a vendor.

    This view allows vendors to delete categories from their menu. It deletes the category 
    with the given primary key.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the category to delete.

    Returns:
        HttpResponse: Redirect to the menu builder view.
    """
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Категорията е изтрита успешно!')
    return redirect('menu_builder')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
    """
    Handle adding a new food item for a vendor.

    This view allows vendors to add new food items to their menu. It handles both GET and 
    POST requests to display the food item form and save the new food item respectively.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered template for adding a food item.
    """
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle, allow_unicode=True)
            form.save()
            messages.success(request, 'Храната е добавена успешно!')
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        # modify this form so it can only takes categories from the logged in vendor
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    """
    Handle editing an existing food item for a vendor.

    This view allows vendors to edit existing food items in their menu. It handles both 
    GET and POST requests to display the food item form and save the updates respectively.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the food item to edit.

    Returns:
        HttpResponse: The rendered template for editing a food item.
    """
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle, allow_unicode=True)
            form.save()
            messages.success(request, 'Храната е обновена успешно!')
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)

    else:
        form = FoodItemForm(instance=food)
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
        'food': food,
    }
    return render(request, 'vendor/edit_food.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food(request, pk=None):
    """
    Handle deleting a food item for a vendor.

    This view allows vendors to delete food items from their menu. It deletes the food 
    item with the given primary key.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the food item to delete.

    Returns:
        HttpResponse: Redirect to the food items by category view.
    """

    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, 'Хранителният артикул е изтрит успешно!')
    return redirect('fooditems_by_category', food.category.id)

def opening_hours(request):
    """
    Display the opening hours view for vendors.

    This view shows the opening hours for the logged-in vendor and allows them to manage 
    their opening hours.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered template for opening hours.
    """
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm()
    context = {
        'form': form,
        'opening_hours': opening_hours,
    }
    return render(request, 'vendor/opening_hours.html', context)

def add_opening_hours(request):
    """
    Handle adding new opening hours for a vendor.

    This view allows vendors to add new opening hours. It handles POST requests with 
    AJAX to save the new opening hours and return a JSON response.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: The JSON response indicating success or failure.
    """
    # handle the data and save them inside the database
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')
            
            try:
                hour = OpeningHour.objects.create(vendor=get_vendor(request), day=day, from_hour=from_hour, to_hour=to_hour, is_closed=is_closed)
                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'is_closed': 'Closed'}
                    else:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'from_hour': hour.from_hour, 'to_hour': hour.to_hour}
                return JsonResponse(response)
            except IntegrityError as e:
                response = {'status': 'failed', 'message': from_hour+'-'+to_hour+' already exists for this day!'}
                return JsonResponse(response)
        else:
            HttpResponse('Invalid request')


def remove_opening_hours(request, pk=None):
    """
    Handle removing opening hours for a vendor.

    This view allows vendors to remove opening hours. It handles AJAX requests to delete 
    the opening hours with the given primary key and return a JSON response.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the opening hours to remove.

    Returns:
        JsonResponse: The JSON response indicating success.
    """
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            hour = get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
            return JsonResponse({'status': 'success', 'id': pk})


def order_detail(request, order_number):
    """
    Display the order detail view for a specific order.

    This view shows the details of a specific order for the logged-in vendor.

    Args:
        request (HttpRequest): The HTTP request object.
        order_number (int): The order number to display details for.

    Returns:
        HttpResponse: The rendered template for order detail.
    """
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        # OrderedFood.objects.filter(...) returns a QuerySet of OrderedFood objects that match the given conditions.
        # order=order specifies that we only want the OrderedFood objects that are associated with the given order order.
        # fooditem__vendor=get_vendor(request) specifies that we only want the OrderedFood objects whose fooditem is associated with the given vendor. 
        # This is achieved by double underlining (__), which allows us to navigate through the relationships between models. In this case, we access the vendor associated with the fooditem.
        ordered_food = OrderedFood.objects.filter(order=order, fooditem__vendor=get_vendor(request))

        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': order.get_total_by_vendor()['subtotal'],
            'tax_data': order.get_total_by_vendor()['tax_dict'],
            'grand_total': order.get_total_by_vendor()['grand_total'],
        }
    except:
        return redirect('vendor')
    return render(request, 'vendor/order_detail.html', context)

def my_orders(request):
    """
    Display the vendor's orders.

    This view shows the orders for the logged-in vendor.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered template for vendor orders.
    """
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'vendor/my_orders.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def update_order_status(request, order_id):
    """
    Update the status of an order.

    This view allows a vendor to update the status of an order they are associated with. 
    The status update is performed via an AJAX POST request containing the new status 
    in the request body. The request must be made by an authenticated vendor.

    Args:
        request (HttpRequest): The HTTP request object.
        order_id (int): The ID of the order to update.

    Returns:
        JsonResponse: A JSON response indicating success or failure.
            - If successful: {'status': 'success'}
            - If invalid status: {'status': 'failed', 'message': 'Invalid status'}
            - If an error occurs: {'status': 'failed', 'message': str(exception)}
            - If the request method is not POST: {'status': 'failed', 'message': 'Invalid request method'}

    Decorators:
        login_required: Ensures that the user is logged in.
        user_passes_test: Ensures that the user is a vendor (checked by `check_role_vendor`).

    Raises:
        Http404: If the order does not exist or the vendor does not have permission to update the order.
    """

    if request.method == 'POST':
        try:
            order = get_object_or_404(Order, id=order_id, vendors__user=request.user)
            data = json.loads(request.body)
            new_status = data.get('status')
            if new_status in dict(Order.STATUS):
                order.status = new_status
                order.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'failed', 'message': 'Invalid status'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)})
    return JsonResponse({'status': 'failed', 'message': 'Invalid request method'})
