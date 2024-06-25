from django import forms

from accounts.validators import allow_only_images_validator
from .models import Category, FoodItem


class CategoryForm(forms.ModelForm):
    """
    Form class for the Category model.

    This form handles the creation and updating of Category instances.

    Attributes:
        Meta (class): Contains metadata for the form, including the model and fields.

    Meta:
        model: Specifies the model associated with the form (Category).
        fields: Specifies the fields to be included in the form ('category_name', 'description').

    Example:
        # When rendering this form, it will include input fields for 'category_name' and 'description'.
        # The form can be used to create or update Category instances.
    """
    class Meta:
        model = Category
        fields = ['category_name', 'description']


class FoodItemForm(forms.ModelForm):
    """
    Form class for the FoodItem model.

    This form handles the creation and updating of FoodItem instances.

    Attributes:
        image (FileField): Custom file input field for the food item image, with validation.
        Meta (class): Contains metadata for the form, including the model and fields.

    Meta:
        model: Specifies the model associated with the form (FoodItem).
        fields: Specifies the fields to be included in the form ('category', 'food_title', 'description', 'price', 'image', 'is_available').

    Example:
        # When rendering this form, it will include input fields for 'category', 'food_title', 'description', 'price', 'image', and 'is_available'.
        # The 'image' field will have a custom class 'btn btn-info w-100' and validation to allow only images.
        # The form can be used to create or update FoodItem instances.
    """
    image = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-100'}), validators=[allow_only_images_validator])
    class Meta:
        model = FoodItem
        fields = ['category', 'food_title', 'description', 'price', 'image', 'is_available']