from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D  # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance

from vendor.models import Vendor, OpeningHour
from menu.models import Category, FoodItem
from accounts.models import UserProfile
from marketplace.models import Cart
from orders.forms import OrderForm
from marketplace.context_processors import get_cart_counter, get_cart_amounts
from datetime import date, datetime

# Create your views here.

def marketplace(request):
    """
    View function for displaying the marketplace with a list of approved vendors.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Rendered HTML page with the list of approved vendors.
    """
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)

def vendor_detail(request, vendor_slug):
    """
    View function for displaying the details of a specific vendor.

    Args:
        request (HttpRequest): The request object.
        vendor_slug (str): The slug of the vendor.

    Returns:
        HttpResponse: Rendered HTML page with the vendor details, categories, and opening hours.
    """
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)

    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset = FoodItem.objects.filter(is_available=True)
        )
    )

    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', '-from_hour')
    
    # Check current day's opening hours.
    today_date = date.today()
    today = today_date.isoweekday()
    
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hours': current_opening_hours,
    }
    return render(request, 'marketplace/vendor_detail.html', context)


def add_to_cart(request, food_id):
    """
    View function to add a food item to the cart.

    Args:
        request (HttpRequest): The request object.
        food_id (int): The ID of the food item.

    Returns:
        JsonResponse: JSON response with the status of the operation.
    """
    # it is checked whether the user is authentic (logged in). This ensures that only registered users can add products to the cart.
    if request.user.is_authenticated:
        # checking if the request was made via AJAX using request.headers.get('x-requested-with'). This helps prevent unwanted access to the function from direct GET requests, assuming that only AJAX requests are valid.
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # checking if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Checking if the user has already added this product to their cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    # If the product has been added and needs to be added again, the amount in the cart is increased
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Increased the cart quantity', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    # the second option is if the product is yet to be added to the cart
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Арикулът е добавен успешно', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Тази храна не съществува в кошницата!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Моля, влезте в профила си, за да продължите!'})


def decrease_cart(request, food_id):
    """
    View function to decrease the quantity of a food item in the cart.

    Args:
        request (HttpRequest): The request object.
        food_id (int): The ID of the food item.

    Returns:
        JsonResponse: JSON response with the status of the operation.
    """
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if chkCart.quantity > 1:
                        # decrease the cart quantity
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse({'status': 'Success', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'Тази храна не съществува в кошницата!'})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Тази храна не съществува!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
        
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Моля, влезте в профила си, за да продължите!'})


@login_required(login_url = 'login')
def cart(request):
    """
    View function to display the user's cart.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Rendered HTML page with the user's cart items.
    """
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)

def delete_cart(request, cart_id):
    """
    View function to delete an item from the cart.

    Args:
        request (HttpRequest): The request object.
        cart_id (int): The ID of the cart item.

    Returns:
        JsonResponse: JSON response with the status of the operation.
    """
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # Check if the cart item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'Success', 'message': 'Артикулът беше изтрит!', 'cart_counter': get_cart_counter(request), 'cart_amount': get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Артикулът в кошницата не същестува!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})


def search(request):
    """
    View function to search for vendors based on user-provided criteria.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Rendered HTML page with the search results or redirects to marketplace if no address is provided.
    """
    # Checking for the presence of an address in the GET request. If 'address' is not considered in the query, the user is redirected to the marketplace page.
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        # Retrieve the parameters from the query
        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        radius = request.GET['radius']
        keyword = request.GET['keyword']

        # Logic for searching for restaurants
        # First, food items (FoodItem) whose titles contain the keyword and are available (is_available=True) are found.
        # The IDs of these vendors are retrieved (values_list('vendor', flat=True)).
        # We are looking for Vendors who either have the found food products or their name contains the keyword, are approved (is_approved=True) and their user accounts are active (user__is_active=True).
        fetch_vendors_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)
        vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
        
        # Filter restaurants by location
        if latitude and longitude and radius:
            # If coordinates and radius are provided, a geometric point (pnt) is created with those coordinates.
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))
            # Restaurants (food providers) are filtered by location so that they are within the specified radius (distance_lte) from the pnt point.
            # annotate(distance=Distance("user_profile__location", pnt)) adds the distance from the point to the restaurant location.
            # order_by("distance") sorts restaurants by distance.
            vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True),
            user_profile__location__distance_lte=(pnt, D(km=radius))
            ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

            # calculates the distance to each merchant in kilometers (v.kms).
            for v in vendors:
                v.kms = round(v.distance.km, 1)

        vendor_count = vendors.count()

        # the necessary information is passed to the visualization template
        context = {
            'vendors': vendors,
            'vendor_count': vendor_count,
            'source_location': address,
        }

        return render(request, 'marketplace/listings.html', context)


@login_required(login_url='login')
def checkout(request):
    """
    View function to display the checkout page with user's cart items and a pre-filled order form.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Rendered HTML page with the checkout form and cart items.
    """
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    }
    form = OrderForm(initial=default_values)
    context = {
        'form': form,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/checkout.html', context)
