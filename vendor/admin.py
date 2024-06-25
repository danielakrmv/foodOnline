from django.contrib import admin
from vendor.models import Vendor, OpeningHour

# Register your models here.
class VendorAdmin(admin.ModelAdmin):
    """
    VendorAdmin class customizes the display and functionality of the Vendor model 
    in the Django admin interface.

    Attributes:
        list_display (tuple): Specifies the fields to be displayed in the list view 
            of the admin panel for the Vendor model. Fields include:
            - 'user': The user associated with the vendor.
            - 'vendor_name': The name of the vendor.
            - 'is_approved': Indicates whether the vendor is approved.
            - 'created_at': The date and time when the vendor was created.
        
        list_display_links (tuple): Specifies which fields in the list view should 
            be clickable links that lead to the detail view of the Vendor model. 
            Fields include:
            - 'user': The user associated with the vendor.
            - 'vendor_name': The name of the vendor.
        
        list_editable (tuple): Specifies which fields can be edited directly in the 
            list view of the Vendor model. Fields include:
            - 'is_approved': Indicates whether the vendor is approved.
    """
    list_display = ('user', 'vendor_name', 'is_approved', 'created_at')
    list_display_links = ('user', 'vendor_name')
    list_editable = ('is_approved',)


class OpeningHourAdmin(admin.ModelAdmin):
    """
    OpeningHourAdmin class customizes the display and functionality of the 
    OpeningHour model in the Django admin interface.

    Attributes:
        list_display (tuple): Specifies the fields to be displayed in the list view 
            of the admin panel for the OpeningHour model. Fields include:
            - 'vendor': The vendor associated with the opening hour.
            - 'day': The day of the week for the opening hour.
            - 'from_hour': The starting time of the opening hour.
            - 'to_hour': The ending time of the opening hour.
    """
    list_display = ('vendor', 'day', 'from_hour', 'to_hour')

admin.site.register(Vendor, VendorAdmin)
admin.site.register(OpeningHour, OpeningHourAdmin)