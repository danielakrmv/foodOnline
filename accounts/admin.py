from django.contrib import admin
from .models import User, UserProfile
from django.contrib.auth.admin import UserAdmin
# Register your models here.

class CustomUserAdmin(UserAdmin):
    """
    CustomUserAdmin is a subclass of Django's UserAdmin class, used to customize the admin interface for the User model.

    Attributes:
        list_display (tuple): Specifies the fields to display in the admin list view for the User model.
        ordering (tuple): Specifies the default ordering of the list view, with '-' indicating descending order.

        These are used to make the password non-editable from the admin panel
        filter_horizontal (tuple): Specifies fields to display with a horizontal filter widget. Currently unused.
        list_filter (tuple): Specifies fields to use for filtering the list view. Currently unused.
        fieldsets (tuple): Specifies the layout of fields on the admin add/change form. Currently unused.
    """
    list_display = ('email', 'first_name', 'last_name', 'username', 'role', 'is_active')
    # '-' means descending order
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)