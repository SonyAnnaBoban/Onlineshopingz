# Generated by Django 5.1.2 on 2024-12-07 10:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Productapp', '0004_product_created_at_product_updated_at_and_more'),
        ('cartapp', '0004_remove_cartitem_variant'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['-popularity', 'product_name']},
        ),
        migrations.RenameField(
            model_name='product',
            old_name='created_at',
            new_name='created_date',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='updated_at',
            new_name='modified_date',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_deleted',
        ),
        migrations.AddField(
            model_name='product',
            name='average_rating',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AddField(
            model_name='product',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='product',
            name='popularity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='product',
            name='stock',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_name',
            field=models.CharField(db_index=True, max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(blank=True, max_length=200, unique=True),
        ),
        migrations.DeleteModel(
            name='ProductVariant',
        ),
    ]
