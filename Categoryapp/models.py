from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    # category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)  # Ensure unique names
    description = models.TextField()
    is_deleted = models.BooleanField(default=False)  # Soft delete
    slug= models.SlugField(max_length=255, unique=True, blank=True)  # Increased max_length

    def save(self, *args, **kwargs):
        # Automatically generate slug if not provided
        if not self.slug:
            self.slug= slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']  # Optional: Order categories by name



