from django.contrib import admin
from .models import Category, FoodItem

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    """
    Admin class for the Category model.

    Configures the display and management of Category instances in the Django admin interface.

    Attributes:
        prepopulated_fields (dict): Automatically populates the 'slug' field based on the 'category_name' field.
        list_display (tuple): Specifies the fields to display in the list view of the admin interface.
        search_fields (tuple): Specifies the fields that can be searched in the admin interface.

    Example:
        # In the admin interface, when you type the category name, the slug field will auto-fill with the category name.
        # The list view will display the category name, associated vendor, and last updated time.
        # You can search categories by their name or vendor's name.

    """
    prepopulated_fields = {'slug': ('category_name',)} # it is used for autofill the slug field when the category name is written
    list_display = ('category_name', 'vendor', 'updated_at')
    search_fields = ('category_name', 'vendor__vendor_name')


class FoodItemAdmin(admin.ModelAdmin):
    """
    Admin class for the FoodItem model.

    Configures the display and management of FoodItem instances in the Django admin interface.

    Attributes:
        prepopulated_fields (dict): Automatically populates the 'slug' field based on the 'food_title' field.
        list_display (tuple): Specifies the fields to display in the list view of the admin interface.
        search_fields (tuple): Specifies the fields that can be searched in the admin interface.
        list_filter (tuple): Adds filters for the specified fields in the admin interface.

    Example:
        # In the admin interface, when you type the food title, the slug field will auto-fill with the food title.
        # The list view will display the food title, associated category, vendor, price, availability status, and last updated time.
        # You can search food items by their title, category name, vendor's name, and price.
        # You can filter the list of food items by their availability status.

    """
    prepopulated_fields = {'slug': ('food_title',)}
    list_display = ('food_title', 'category', 'vendor', 'price', 'is_available', 'updated_at')
    search_fields = ('food_title', 'category__category_name', 'vendor__vendor_name', 'price')
    list_filter = ('is_available',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem, FoodItemAdmin)
