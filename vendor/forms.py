from django import forms
from .models import Vendor, OpeningHour
from accounts.validators import allow_only_images_validator


class VendorForm(forms.ModelForm):
    """
    VendorForm is a Django ModelForm for the Vendor model, designed to handle 
    the creation and update of vendor instances.

    Fields:
        vendor_license (forms.FileField): A file field for uploading the vendor's 
            license. It uses a custom widget and a validator to ensure only image 
            files are uploaded.

    Meta:
        model (Vendor): Specifies that this form is for the Vendor model.
        fields (list): Specifies the fields from the Vendor model to include in 
            the form. These fields are:
            - 'vendor_name': The name of the vendor.
            - 'vendor_license': The license of the vendor, which is an image file.
    """
    vendor_license = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_images_validator])
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']


class OpeningHourForm(forms.ModelForm):
    """
    OpeningHourForm is a Django ModelForm for the OpeningHour model, designed to 
    handle the creation and update of opening hour instances for vendors.

    Meta:
        model (OpeningHour): Specifies that this form is for the OpeningHour model.
        fields (list): Specifies the fields from the OpeningHour model to include 
            in the form. These fields are:
            - 'day': The day of the week for the opening hour.
            - 'from_hour': The starting time of the opening hour.
            - 'to_hour': The ending time of the opening hour.
            - 'is_closed': Indicates whether the vendor is closed on the specified day.
    """
    class Meta:
        model = OpeningHour
        fields = ['day', 'from_hour', 'to_hour', 'is_closed']