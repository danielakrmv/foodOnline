from django.contrib import admin
from .models import Cart, Tax

class CartAdmin(admin.ModelAdmin):
    """
    Customizes the display of Cart model entries in the Django admin interface.

    Attributes:
        list_display (tuple): Specifies the fields to display in the list view
                              of the Cart model in the admin interface.
                              Includes 'user', 'fooditem', 'quantity', and 'updated_at'.
    """
    list_display = ('user', 'fooditem', 'quantity', 'updated_at')


class TaxAdmin(admin.ModelAdmin):
    """
    Customizes the display of Tax model entries in the Django admin interface.

    Attributes:
        list_display (tuple): Specifies the fields to display in the list view
                              of the Tax model in the admin interface.
                              Includes 'tax_type', 'tax_percentage', 'tax_value', and 'is_active'.
    """
    list_display = ('tax_type', 'tax_percentage', 'tax_value', 'is_active')


admin.site.register(Cart, CartAdmin)
admin.site.register(Tax, TaxAdmin)