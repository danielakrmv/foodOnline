from django.contrib import admin
from .models import Payment, Order, OrderedFood

class OrderedFoodInline(admin.TabularInline):
    model = OrderedFood
    readonly_fields = ('order', 'payment', 'user', 'fooditem', 'quantity', 'price', 'amount') # These fields will be displayed as read-only in the admin interface. It ensures that once an order is placed, these details cannot be modified directly from the admin interface.
    extra = 0 # This specifies that no extra empty forms should be displayed by default.


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'name', 'phone', 'email', 'total', 'payment_method', 'status', 'order_placed_to', 'is_ordered']
    inlines = [OrderedFoodInline]

# Register your models here.
admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedFood)