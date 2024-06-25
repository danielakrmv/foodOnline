from django.shortcuts import render, redirect

from vendor.forms import VendorForm
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages, auth
from .utils import detectUser, send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
# from django.template.defaultfilters import slugify
from django.utils.text import slugify
from vendor.models import Vendor
from orders.models import Order

import datetime

# Create your views here.

# Restrict the vendor from accessing the custom page
def check_role_vendor(user):
    """
    Restricts access to vendor-specific pages.

    Args:
        user (User): The user object.

    Returns:
        bool: True if the user is a vendor, otherwise raises PermissionDenied.
    """
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

# Restrict the customer from accessing the vendor page 
def check_role_customer(user):
    """
    Restricts access to customer-specific pages.

    Args:
        user (User): The user object.

    Returns:
        bool: True if the user is a customer, otherwise raises PermissionDenied.
    """
    if user.role == 2:
        return True
    else:
        raise PermissionDenied

def registerUser(request):
    """
    Handles user registration and email verification.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The rendered template for user registration.
    """
    if request.user.is_authenticated:
        messages.warning(request, 'Вие вече сте в профила си!')
        return redirect('dashboard')
    elif request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            # Create the user using the form

            # password = form.cleaned_data['password']
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()

            # Create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.CUSTOMER
            user.save()

            # Send verification email
            mail_subject = 'Моля, активирайте своя акаунт!'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Вашият акаунт беше регистриран успешно! Проверете имейла си за активиране!')
            return redirect('registerUser')

        else:
            print(form.errors)
    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/registerUser.html', context)

def registerVendor(request):
    """
    Handles vendor registration, vendor profile creation, and email verification.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The rendered template for vendor registration.
    """
    if request.user.is_authenticated:
        messages.warning(request, 'Вие вече сте в профила си!')
        return redirect('myAccount')
    elif request.method == 'POST':
        # store the data and create the user
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)

        if form.is_valid() and v_form.is_valid:

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor_name = v_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name, allow_unicode=True)+'-'+str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            # Send verification email
            mail_subject = 'Моля активирайте своя акаунт'
            email_template = 'accounts/emails/vendor_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Вашият акаунт беше регистриран успешно! Моля, проверете имейла си за активиращ линк и изчакайте одобрение от нашия администратор.')
            return redirect('registerVendor')

        else:
            print('Invalid form!')
            print(form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()

    context = {
        'form': form,
        'v_form': v_form,
    }

    return render(request, 'accounts/registerVendor.html', context)

def activate(request, uidb64, token):
    """
    Activates user accounts via email verification links.

    Args:
        request (HttpRequest): The request object.
        uidb64 (str): Base64 encoded user ID.
        token (str): Token for validating the user.

    Returns:
        HttpResponse: Redirects to the account page with success or error messages.
    """
    # Activate the user by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Поздравления! Вашият акаунт е активиран!.')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('myAccount')

def login(request):
    """
    Handles user login.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Redirects to the appropriate dashboard or re-renders the login page with errors.
    """

    if request.user.is_authenticated:
        messages.warning(request, 'Вече сте в профила си!')
        return redirect('myAccount')
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Влязохте в профила си.')
            return redirect('myAccount')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')

    return render(request, 'accounts/login.html')

def logout(request):
    """
    Logs out the user.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Redirects to the login page with an informational message.
    """
    auth.logout(request)
    messages.info(request, 'Излязохте от профила си.')
    return redirect('login')

@login_required(login_url='login')
def myAccount(request):
    """
    Redirects users to their respective dashboards based on their roles.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Redirects to the appropriate dashboard.
    """
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):
    """
    Renders the customer dashboard view.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The rendered template for the customer dashboard.
    """
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    recent_orders = orders.order_by('-created_at')[:5]

    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/custDashboard.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    """
    Renders the vendor dashboard view, including order and revenue data.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The rendered template for the vendor dashboard.
    """
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
    recent_orders = orders[:5]

    # current month's revenue
    current_month = datetime.datetime.now().month
    current_month_orders = orders.filter(vendors__in=[vendor.id], created_at__month=current_month)
    current_month_revenue = 0
    for i in current_month_orders:
        current_month_revenue += i.get_total_by_vendor()['grand_total']
    

    # total revenue
    total_revenue = 0
    for i in orders:
        total_revenue += i.get_total_by_vendor()['grand_total']

    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent_orders': recent_orders,
        'total_revenue': total_revenue,
        'current_month_revenue': current_month_revenue,
    }
    return render(request, 'accounts/vendorDashboard.html', context)


def forgot_password(request):
    """
    Handles password reset requests by sending reset links via email.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The rendered template for the forgot password page or redirects to the login page with messages.
    """

    if request.method == 'POST':
        email = request.POST['email']

        # Check if the email exists in the database
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = 'Възстановете своята парола'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Линк за обновяване на паролата беше изпратен.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')

def reset_password_validate(request, uidb64, token):
    """
    Validates the password reset link and user.

    Args:
        request (HttpRequest): The request object.
        uidb64 (str): Base64 encoded user ID.
        token (str): Token for validating the user.

    Returns:
        HttpResponse: Redirects to the password reset page or account page with messages.
    """

    # validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # save uid inside the current session
        request.session['uid'] = uid
        messages.info(request, 'Моля обновете вашата парола!')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('myAccount')

def reset_password(request):
    """
    Handles password reset form submissions.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: Redirects to the login page with a success message or re-renders the reset password page with errors.
    """
    
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Паролата е обновена успешно!')
            return redirect('login')
        else:
            messages.error(request, 'Паролата не е обновена!')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')