
from django.db import models
from django.conf import settings  # Import settings to use the custom user model
from Productapp.models import Product  # Import the Product model

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # Use the custom user model
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.email}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=0)

    @property
    def total_price(self):
        """
        Calculate the total price for the cart item based on the product's price
        and the quantity of this item in the cart.
        """
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.product_name} (x{self.quantity})"
