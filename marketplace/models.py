from django.db import models
from accounts.models import User
from menu.models import FoodItem

# Create your models here.
class Cart(models.Model):
    """
    A model representing a shopping cart item.

    Attributes:
        user (ForeignKey): A reference to the user who owns the cart item.
        fooditem (ForeignKey): A reference to the food item in the cart.
        quantity (PositiveIntegerField): The quantity of the food item in the cart.
        created_at (DateTimeField): The timestamp when the cart item was created.
        updated_at (DateTimeField): The timestamp when the cart item was last updated.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        """
        Returns the string representation of the cart item, which is the username of the user who owns the cart.

        Returns:
            str: The username of the user.
        """
        return self.user

class Tax(models.Model):
    """
    A model representing a tax.

    Attributes:
        tax_type (CharField): The type of the tax (e.g., VAT, Delivery).
        tax_percentage (DecimalField): The percentage of the tax (e.g., 20.00 for 20%).
        tax_value (DecimalField): The fixed value of the tax.
        is_active (BooleanField): A flag indicating whether the tax is active or not.
    """
    tax_type = models.CharField(max_length=20, unique=True)
    tax_percentage = models.DecimalField(decimal_places=2, max_digits=4, blank=True, verbose_name='Tax Percentage (%)')
    tax_value = models.DecimalField(decimal_places=2, max_digits=4, blank=True, default=0.0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'tax'

    def __str__(self):
        """
        Returns the string representation of the tax, which is the tax type.

        Returns:
            str: The type of the tax.
        """
        return self.tax_type