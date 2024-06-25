import re
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.fields.related import OneToOneField

from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point

# Base User Manager will allow to edit the way how the users and super users are created.
class UserManager(BaseUserManager):
    """
    Custom manager for User model.

    This manager defines methods for creating users and superusers.
    It handles the normalization of email addresses and provides functionality 
    to save the user instances to the database.

    Methods:
    create_user(first_name, last_name, username, email, password=None): 
        Creates and saves a regular user with the given details.
    create_superuser(first_name, last_name, username, email, password=None): 
        Creates and saves a superuser with the given details and admin privileges.
    """

    def create_user(self, first_name, last_name, username, email, password=None):
        """
        Create and return a regular user with the given email, username, first name, 
        last name, and password.

        Args:
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str, optional): The password for the user. Defaults to None.

        Raises:
        ValueError: If the email or username is not provided.

        Returns:
        User: A User instance representing the created user.
        """
        if not email:
            raise ValueError('User must have an email!')
        
        if not username:
            raise ValueError('User must have an username!')
        
        
        user = self.model(
            # normalize email it will take the email address from me and if this address is with uppercase letters it will convert them to lowercase.
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)

        # Django by default uses using parameter to define which database the manager should use for the operations.
        # this is in cases if we have multiple databases
        # in this case I have only one database and self._db will take the default database from the config.
        user.save(using=self._db)

        return user
    
    def create_superuser(self, first_name, last_name, username, email, password=None):
        """
        Create and return a superuser with the given email, username, first name, 
        last name, and password. The superuser will have admin privileges.

        Args:
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str, optional): The password for the user. Defaults to None.

        Returns:
        User: A User instance representing the created superuser.
        """
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
            password = password,
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)

        return user


# with the Abstract Base User we have full control of editing the whole custom user model, including the authentication functionality
class User(AbstractBaseUser):
    """
    Custom user model.

    This model extends Django's AbstractBaseUser to allow for a fully customizable user model.
    It includes fields for storing user details and flags for user permissions.

    Attributes:
    first_name (str): The first name of the user.
    last_name (str): The last name of the user.
    username (str): The username of the user.
    email (str): The email address of the user.
    phone_number (str): The phone number of the user.
    role (int): The role of the user, either Vendor or Customer.
    date_joined (datetime): The date and time when the user joined.
    last_login (datetime): The date and time when the user last logged in.
    created_date (datetime): The date and time when the user was created.
    modified_date (datetime): The date and time when the user was last modified.
    is_admin (bool): Whether the user has admin rights.
    is_staff (bool): Whether the user is a staff member.
    is_active (bool): Whether the user account is active.
    is_superadmin (bool): Whether the user has superadmin rights.

    Methods:
    __str__(): Returns the string representation of the user.
    has_perm(perm, obj=None): Returns True if the user has the specified permission.
    has_module_perms(app_label): Returns True if the user has permissions for the specified app.
    get_role(): Returns the role of the user as a string.
    """
    VENDOR = 1
    CUSTOMER = 2

    ROLE_CHOICE = (
        (VENDOR, 'Vendor'),
        (CUSTOMER, 'Customer'),
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=12, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICE, blank=True, null=True)

    # required fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    # for authentication we want to use the email (not the username that Abstract class use by default)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        """
        Return the string representation of the user, which is their email address.
        """
        return self.email
    
    def has_perm(self, perm, obj=None):
        """
        Check if the user has a specific permission.

        Args:
        perm (str): The name of the permission.
        obj (object, optional): The object for which the permission is required.

        Returns:
        bool: True if the user has the permission, False otherwise.
        """
        return self.is_admin
    
    def has_module_perms(self, app_label):
        """
        Check if the user has permissions for a specific app.

        Args:
        app_label (str): The label of the app.

        Returns:
        bool: True if the user has permissions for the app, False otherwise.
        """
        return True
    
    def get_role(self):
        """
        Return the role of the user as a string.

        Returns:
        str: 'Vendor' if the user is a vendor, 'Customer' if the user is a customer.
        """
        if self.role == 1:
            user_role = 'Vendor'
        elif self.role == 2:
            user_role = 'Customer'
        return user_role
    

class UserProfile(models.Model):
    """
    User profile model.

    This model extends the user model to include additional information about the user.
    It includes fields for storing profile pictures, cover photos, address, and location details.

    Attributes:
    user (OneToOneField): A one-to-one relationship with the User model.
    profile_picture (ImageField): The profile picture of the user.
    cover_photo (ImageField): The cover photo of the user.
    address (str): The address of the user.
    country (str): The country of the user.
    state (str): The state of the user.
    city (str): The city of the user.
    pin_code (str): The postal code of the user.
    latitude (str): The latitude of the user's location.
    longitude (str): The longitude of the user's location.
    location (PointField): The geographic point of the user's location.
    created_at (datetime): The date and time when the profile was created.
    modified_at (datetime): The date and time when the profile was last modified.

    Methods:
    __str__(): Returns the string representation of the user profile, which is the user's email.
    save(*args, **kwargs): Saves the user profile, setting the location point if latitude and longitude are provided.
    """
    # one user can have only one user profile - if we want many profiles (use ForeignKey)
    # on_delete option means when the user is deleted his profile also should be deleted
    user = OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='users/profile_pictures', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='users/cover_photos', blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    country = models.CharField(max_length=15, blank=True, null=True)
    state = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    pin_code = models.CharField(max_length=4, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    location = gismodels.PointField(blank=True, null=True, srid=4326)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # def full_address(self):
    #     return f'{self.address_line_1}, {self.address_line_2}'

    def __str__(self):
        """
        Return the string representation of the user profile, which is the user's email.
        """
        return self.user.email
    
    def save(self, *args, **kwargs):
        """
        Save the user profile, setting the location point if latitude and longitude are provided.

        Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        """
        if self.latitude and self.longitude:
            self.location = Point(float(self.longitude), float(self.latitude))
            return super(UserProfile, self).save(*args, **kwargs)
        return super(UserProfile, self).save(*args, **kwargs)
