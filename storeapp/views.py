
from django.shortcuts import render, get_object_or_404
from Productapp.models import Product, ProductImage
from django.utils.timezone import now


def product_list(request):
    # Get filter and sort options from the request
    category = request.GET.get('category')  # Filter by category (if provided)
    sort_option = request.GET.get('sort', 'new')  # Default sort: new arrivals

    # Base queryset
    products = Product.objects.filter(is_available=True, stock__gt=0)

    # Filter by category if provided
    if category:
        products = products.filter(category__slug=category)

    # Sorting logic
    if sort_option == 'popularity':
        products = products.order_by('-popularity')
    elif sort_option == 'price_low_to_high':
        products = products.order_by('price')
    elif sort_option == 'price_high_to_low':
        products = products.order_by('-price')
    elif sort_option == 'average_rating':
        products = products.order_by('-average_rating')
    elif sort_option == 'a_to_z':
        products = products.order_by('product_name')
    elif sort_option == 'z_to_a':
        products = products.order_by('-product_name')
    elif sort_option == 'new':
        products = products.order_by('-created_date')

    # Render the template with the products
    return render(request, 'products/product_list.html', {'products': products})



def product_detail(request, category_slug, product_slug):
    # Retrieve the specific product by slug and category_slug (ensuring it's not deleted)
    product = get_object_or_404(Product, slug=product_slug, category__slug=category_slug, is_deleted=False)
    
    # Get related products from the same category, excluding the current product
    related_products = Product.objects.filter(
        category=product.category,
        is_deleted=False,
        is_available=True
    ).exclude(id=product.id)[:4]
    
    # Fetch all images associated with the product
    product_images = ProductImage.objects.filter(product=product)
    
    # Check if there are any active discounts for the product
    discount = product.discounts.filter(
        start_date__lte=now(),
        end_date__gte=now()
    ).first() if hasattr(product, 'discounts') else None
    
    # Calculate the final price considering any discount
    final_price = product.price
    if discount:
        final_price -= (product.price * discount.percentage / 100)

    return render(request, 'Userside/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'product_images': product_images,
        'discount': discount,
        'final_price': final_price,
    })


def product_search(request):
    query = request.GET.get('q', '')  # Get the search query from the GET parameters
    products = Product.objects.filter(product_name__icontains=query)  # Search for products by name

    return render(request, 'Userside/product_list.html', {
        'products': products,
        'query': query,
    })
