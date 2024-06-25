import re
from django import forms
from .models import User, UserProfile
from .validators import allow_only_images_validator


class UserForm(forms.ModelForm):
    """
    Form for registering users in the application.

    This form inherits from ModelForm and is designed for creating and validating users.
    It includes additional fields for password and password confirmation, as well as specific
    checks for password complexity.

    Attributes:
        password (CharField): Field for entering the password, using PasswordInput to hide the entered characters.
        confirm_password (CharField): Field for confirming the password, using PasswordInput to hide the entered characters.

    Meta:
        model (User): The model associated with this form.
        fields (list): List of model fields to include in the form.

    Methods:
        clean(): Performs additional validation of the form data.
    """

    # Field for entering a password, using PasswordInput to hide the entered characters.
    password = forms.CharField(widget=forms.PasswordInput())

    # Field for confirming the password, also using PasswordInput.
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    # Defining the Meta Class:
    class Meta:
        # Associates the form with the User model.
        model = User
        # Specifies which model fields will be included in the form.
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def clean(self):
        """
        Performs additional validation of the form data.

        Checks if the password is at least 8 characters long, contains at least one digit,
        one uppercase letter, one lowercase letter, and one special character. Also verifies
        that the password and confirmation password fields match.

        Raises:
            forms.ValidationError: If any of the password requirements are not met or if the passwords do not match.
        """
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long!')
        if not re.search(r'\d', password):
            raise forms.ValidationError('Password must contain at least one digit!')
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('Password must contain at least one uppercase letter!')
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError('Password must contain at least one lowercase letter!')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError('Password must contain at least one special character!')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match!"
            )


class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile information.

    This form inherits from ModelForm and is designed for updating user profile details.
    It includes fields for profile picture, cover photo, address, and location information,
    with additional widgets and validation for file fields.

    Attributes:
        address (CharField): Field for entering the address with a placeholder and required attribute.
        profile_picture (FileField): Field for uploading a profile picture with a custom CSS class and image validation.
        cover_photo (FileField): Field for uploading a cover photo with a custom CSS class and image validation.

    Meta:
        model (UserProfile): The model associated with this form.
        fields (list): List of model fields to include in the form.

    Methods:
        __init__(*args, **kwargs): Custom initialization for setting read-only attributes for latitude and longitude fields.
    """
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Start typing...', 'required': 'required'}))
    profile_picture = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_images_validator])
    cover_photo = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_images_validator])
    
    # latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    # longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'cover_photo', 'address', 'country', 'state', 'city', 'pin_code', 'latitude', 'longitude']

    def __init__(self, *args, **kwargs):
        """
        Custom initialization for the form.

        This method sets the 'readonly' attribute for the latitude and longitude fields to make them non-editable.
        """
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'latitude' or field == 'longitude':
                self.fields[field].widget.attrs['readonly'] = 'readonly'


class UserInfoForm(forms.ModelForm):
    """
    Form for updating basic user information.

    This form inherits from ModelForm and is designed for updating basic user details such as first name,
    last name, and phone number.

    Meta:
        model (User): The model associated with this form.
        fields (list): List of model fields to include in the form.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']