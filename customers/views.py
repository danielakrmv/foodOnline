from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from accounts.forms import UserProfileForm, UserInfoForm
from accounts.models import UserProfile
from django.contrib import messages
from orders.models import Order, OrderedFood
import simplejson as json

# Create your views here.
@login_required(login_url='login')
def cprofile(request):
    """
    View for displaying and updating customer profile information.

    GET: Renders the profile update form.
    POST: Handles form submission and updates the profile information.

    Returns:
        Renders the customer profile page.
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Профилът е обновен!')
            return redirect('cprofile')
        else:
            print(profile_form.errors)
            print(user_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)

    context = {
        'profile_form': profile_form,
        'user_form' : user_form,
        'profile': profile,
    }
    return render(request, 'customers/cprofile.html', context)

def my_orders(request):
    """
    View for displaying a list of customer orders.

    Returns:
        Renders the page with a list of customer orders.
    """
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'customers/my_orders.html', context)

def order_detail(request, order_number):
    """
    View for displaying details of a specific customer order.

    Args:
        order_number: The order number to retrieve details for.

    Returns:
        Renders the page with details of the specified order.
    """
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)
        tax_data = json.loads(order.tax_data)
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'customers/order_detail.html', context)
    except:
        return redirect('customer')