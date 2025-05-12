
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now
from Categoryapp.models import Category
from django.core.exceptions import ValidationError

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)  # Tracks stock availability
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    popularity = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # For sorting by popularity
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0, 
                                         validators=[MinValueValidator(0), MaxValueValidator(5)])
    is_available = models.BooleanField(default=True)  # Indicates whether the product is available for sale
    created_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    modified_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.product_name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_name

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def is_in_stock(self):
        """Check if the product is in stock."""
        return self.stock > 0

    def get_active_discounts(self):
        # Fetch active discounts for this product
        return self.discounts.filter(start_date__lte=now(), end_date__gte=now())

    def get_final_price(self):
        # Assuming you want to get the price after applying any active discount
        discounts = self.get_active_discounts()
        final_price = self.price
        for discount in discounts:
            final_price -= final_price * (discount.percentage / 100)
        return final_price

    def reduce_stock(self, quantity):
        """Reduce stock when a product is purchased."""
        if quantity > self.stock:
            raise ValueError("Not enough stock available.")
        self.stock -= quantity
        self.is_available = self.stock > 0
        self.save()

    class Meta:
        ordering = ['-popularity', 'product_name']  # Default ordering by popularity, then alphabetically

# Adding an image model for the product
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f"Image of {self.product.product_name}"

class Discount(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='discounts')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='discounts')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def is_active(self):
        return self.start_date <= now() <= self.end_date

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date.")

    def __str__(self):
        return f"{self.name} - {self.percentage}%"
