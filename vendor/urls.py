from django.urls import path, include
from . import views
from accounts import views as AccountViews

"""
This module defines URL patterns for the vendor app. It includes paths for various views 
related to vendor dashboard, profile management, menu building, category and food item 
CRUD operations, opening hours management, and order details.

URLs:
    - '' : Redirects to the vendor dashboard.
    - 'profile/' : Redirects to the vendor profile view.
    - 'menu-builder/' : Redirects to the menu builder view.
    - 'menu-builder/category/<int:pk>/' : Displays food items by category.
    - 'menu-builder/category/add/' : Adds a new category.
    - 'menu-builder/category/edit/<int:pk>/' : Edits an existing category.
    - 'menu-builder/category/delete/<int:pk>/' : Deletes a category.
    - 'menu-builder/food/add/' : Adds a new food item.
    - 'menu-builder/food/edit/<int:pk>/' : Edits an existing food item.
    - 'menu-builder/food/delete/<int:pk>/' : Deletes a food item.
    - 'opening-hours/' : Displays the opening hours view.
    - 'opening-hours/add/' : Adds new opening hours.
    - 'opening-hours/remove/<int:pk>/' : Removes opening hours.
    - 'order_detail/<int:order_number>/' : Displays the order detail view.
    - 'my_orders/' : Displays the vendor's orders.

Imports:
    - path: Function to define URL patterns.
    - include: Function to include other URL configurations.
    - views: The views module from the current app.
    - AccountViews: The views module from the accounts app.
"""


urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendor'),
    path('profile/', views.vprofile, name='vprofile'),
    path('menu-builder/', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>/', views.fooditems_by_category, name='fooditems_by_category'),

    # Category CRUD
    path('menu-builder/category/add/', views.add_category, name='add_category'),
    path('menu-builder/category/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('menu-builder/category/delete/<int:pk>/', views.delete_category, name='delete_category'),

    # Food item CRUD
    path('menu-builder/food/add/', views.add_food, name='add_food'),
    path('menu-builder/food/edit/<int:pk>/', views.edit_food, name='edit_food'),
    path('menu-builder/food/delete/<int:pk>/', views.delete_food, name='delete_food'),

    # Opening Hours CRUD
    path('opening-hours/', views.opening_hours, name='opening_hours'),
    path('opening-hours/add/', views.add_opening_hours, name='add_opening_hours'),
    path('opening-hours/remove/<int:pk>/', views.remove_opening_hours, name='remove_opening_hours'),

    path('order_detail/<int:order_number>/', views.order_detail, name='vendor_order_detail'),
    path('my_orders/', views.my_orders, name='vendor_my_orders'),
]