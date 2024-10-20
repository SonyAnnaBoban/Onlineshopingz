from django.db import models
from django.utils.text import slugify
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_deleted = models.BooleanField(default=False)  # Soft delete
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

