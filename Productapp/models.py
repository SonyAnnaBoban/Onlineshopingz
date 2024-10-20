from django.db import models
from django.utils.text import slugify
from  Categoryapp.models import Category

class Product(models.Model):
    product_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)  # Soft delete


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.product_name)  # Fixed to use product_name
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_name
