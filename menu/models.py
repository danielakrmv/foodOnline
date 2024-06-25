# from tabnanny import verbose
from django.db import models
from vendor.models import Vendor


class Category(models.Model):
    """
    Represents a category of food items offered by a vendor.

    Attributes:
        vendor (ForeignKey): A reference to the Vendor who owns this category. 
                             When the Vendor is deleted, this category is also deleted.
        category_name (CharField): The name of the category, with a maximum length of 50 characters.
        slug (SlugField): A unique slug for the category, used in URLs (e.g., if the category name is 'Sea Food', 
                          the slug might be 'sea-food').
        description (TextField): A brief description of the category, optional with a maximum length of 250 characters.
        created_at (DateTimeField): The date and time when the category was created, automatically set on creation.
        updated_at (DateTimeField): The date and time when the category was last updated, automatically set on each update.

    Methods:
        clean: Capitalizes the category name before saving.
        __str__: Returns the category name as its string representation.

    Meta:
        verbose_name: The singular name for this model in the admin interface.
        verbose_name_plural: The plural name for this model in the admin interface.
    """

    # when Vendor is deleted this particular category is also deleted
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True) # this means the url of this particular category (if the category is sea food the slug will be sea-food)
    description = models.TextField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def clean(self):
        self.category_name = self.category_name.capitalize()
    
    def __str__(self):
        return self.category_name


class FoodItem(models.Model):
    """
    Represents a food item offered by a vendor within a specific category.

    Attributes:
        vendor (ForeignKey): A reference to the Vendor who offers this food item.
        category (ForeignKey): A reference to the Category this food item belongs to.
                               When the Category is deleted, this food item is also deleted.
        food_title (CharField): The title of the food item, with a maximum length of 50 characters.
        slug (SlugField): A unique slug for the food item, used in URLs.
        description (TextField): A brief description of the food item, optional with a maximum length of 250 characters.
        price (DecimalField): The price of the food item, with a maximum of 10 digits and 2 decimal places.
        image (ImageField): An image of the food item, uploaded to the 'foodimages' directory.
        is_available (BooleanField): A flag indicating whether the food item is currently available, defaulting to True.
        created_at (DateTimeField): The date and time when the food item was created, automatically set on creation.
        updated_at (DateTimeField): The date and time when the food item was last updated, automatically set on each update.

    Methods:
        __str__: Returns the food title as its string representation.
    """
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='fooditems')
    food_title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100)
    description = models.TextField(max_length=250, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='foodimages')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.food_title
