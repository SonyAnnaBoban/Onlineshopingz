from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, CartItem
from Productapp.models import Product
from decimal import Decimal
from userprofileapp.models import UserAddress

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_deleted=False)

    # Get the quantity from the POST request, default to 1 if not provided
    quantity = int(request.POST.get('quantity',1))

    # Check if the requested quantity exceeds the product's available stock
    if quantity > product.stock:
        messages.error(request, f"Only {product.stock} units of {product.product_name} are available.")
        return redirect('productapp:product_detail', product_id=product_id)

    # Get or create the cart for the logged-in user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Get or create the cart item for the specific product
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        # If the item already exists in the cart, update its quantity
        if cart_item.quantity + quantity > product.stock:
            messages.error(request, f"Adding {quantity} units exceeds available stock.")
            return redirect('productapp:product_detail', product_id=product_id)
        cart_item.quantity += quantity
    else:
        # Set the quantity for a new cart item
        cart_item.quantity = quantity

    cart_item.save()
    messages.success(request, f"{product.product_name} has been added to your cart.")
    return redirect('cartapp:view_cart')


@login_required
def view_cart(request):
    # Get the current user's cart
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = cart.items.all() if cart else []
  

    # Calculate total price and total quantity
    total_price = sum(item.total_price for item in cart_items)
    total_quantity = sum(item.quantity for item in cart_items)  # Total number of items in the cart

    return render(request, 'Userside/view_cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_quantity': total_quantity,
    })


@login_required
def remove_from_cart(request, item_id):
    # Fetch the specific cart item belonging to the current user
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()

    messages.success(request, "Item removed from your cart.")
    return redirect('cartapp:view_cart')
from django.http import JsonResponse
@login_required
def update_cart_item(request, product_id,quantity):
    product = get_object_or_404(Product, id=product_id, is_deleted=False)
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    

    print("quantity:",quantity)
    # Validate the new quantity
    try:
        new_quantity = int(quantity)

        if new_quantity < 1:
            return JsonResponse({'success': False, 'message': 'Quantity must be at least 1.'})

        if new_quantity > product.stock:
            return JsonResponse({'success': False, 'message': f"Only {product.stock} units available."})

        cart_item.quantity = new_quantity
        cart_item.save()

     
        carts = Cart.objects.filter(user=request.user).first()
        cart_items = carts.items.all() if cart else []
        # total_price = sum(item.total_price for item in cart_item)  #	Total cost of all items in the cart
        # total_quantity = sum(item.quantity for item in cart_item) #Total number of items (e.g. 3 products)
        cart_total = sum(item.total_price for item in cart_items)
        item_total = cart_item.quantity * product.price
        return JsonResponse({
            'success': True,
            'item_total': item_total,
            'cart_total': cart_total,
        })    
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Invalid quantity.'})

   








def get_cart_items_and_total(user):
   
    cart_items = []
    cart_total = Decimal('0.00')

    try:
        # Access the user's cart
        cart = user.cart
        for item in cart.items.all():
            item_total = item.product.price * item.quantity
            cart_total += item_total
            cart_items.append({
                'product_name': item.product.product_name,
                'product_image_url': item.product.images.first().image.url if item.product.images.exists() else '',
                'quantity': item.quantity,
                'price': item.product.price,
                'item_total': item_total,
            })
    except Cart.DoesNotExist:
        # Handle cases where the user does not have a cart
        cart_items = []
        cart_total = Decimal('0.00')

    return cart_items, cart_total



@login_required
def checkout(request):
    if request.method == 'GET':
    #     selected_address_id = request.POST.get('selected_address')
    #     payment_method = request.POST.get('payment_method')
    #     confirm_same = request.POST.get('confirm_same')  # This is from a confirmation checkbox/radio
    #     print("Selected address:", selected_address_id)
    #     # Validate the address
    #     address = get_object_or_404(UserAddress, id=selected_address_id, user=request.user)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
    #     if not confirm_same:
    #         messages.warning(request, "Please confirm the selected address will be used as the shipping address.")
    #         return redirect('userprofileapp:manage_addresses')

    #     # Save selection in session
    #     request.session['checkout_data'] = {
    #         'address_id': address.id,
    #         'payment_method': payment_method,
    #     }

    #     return redirect('orderapp:place_order')

    # else:
        # Get user addresses and cart details
        addresses = UserAddress.objects.filter(user=request.user)
     
        cart_items, cart_total = get_cart_items_and_total(request.user)

        if not addresses.exists():
            messages.warning(request, "Please add a shipping address before proceeding.")
            return redirect('userprofileapp:manage_addresses')
          
        return render(request, 'Userside/checkout.html', {
            'saved_addresses': addresses,
            'cart_items': cart_items,
            'cart_total': cart_total,
        })



