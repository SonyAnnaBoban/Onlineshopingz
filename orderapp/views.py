from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from django.http import JsonResponse
from cartapp.models import Cart,CartItem
from Productapp.models import Product, Discount
from userprofileapp.models import UserAddress
from .models import Order, OrderItem, OrderAddress
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

@login_required
def cancel_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status in ['Pending', 'Processing']:
            order.status = 'Cancelled'
            order.save()
            return JsonResponse({'status': 'success', 'message': 'Order cancelled successfully'})
        else:
            return JsonResponse({'status': 'fail', 'message': 'Order cannot be cancelled at this stage'}, status=400)
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'}, status=405)


@login_required

@csrf_exempt  
def place_order(request):
    if request.method == 'POST':
        address_id = request.POST.get('selected_address')
        payment_method = request.POST.get('payment_method')

        if not address_id or not payment_method:
            return JsonResponse({'success': False, 'message': 'Please select a shipping address and payment method.'})

        try:
            selected_address = UserAddress.objects.get(id=address_id, user=request.user)
        except UserAddress.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Selected address is not valid.'})

        cart = Cart.objects.filter(user=request.user).first()
        if not cart  or not cart.items.exists():
            return JsonResponse({'success': False, 'message': 'Your cart is empty.'})

        cart_items = cart.items.all()
        cart_total = sum(item.product.price * item.quantity for item in cart_items)

        order = Order.objects.create(
            user=request.user,
            total_price=cart_total,
            payment_method=payment_method,
            status='Pending',
            order_date=now(),
        )

        OrderAddress.objects.create(
            order=order,
            name=selected_address.name,
            address_line1=selected_address.address_line1,
            city=selected_address.city,
            state=selected_address.state,
            zip_code=selected_address.zip_code,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
            item.product.stock -= item.quantity
            item.product.save()

        cart.items.all().delete()
        cart.delete()

        return JsonResponse({
            'success': True,
            'message': 'Your order has been placed successfully!',
            'order_id': order.id,
            'order_total': cart_total,
            'redirect_url': '/order/success/'  # optional: for JS to redirect
        })

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
#####################################################

@login_required
def order_success(request):
    order = Order.objects.filter(user=request.user).order_by('-order_date').first()

    if not order:
        messages.error(request, "No recent orders found.")
        return redirect('Accountsapp:home')

    return render(request, 'Userside/sucess.html', {'order': order})

@login_required
# def order_history(request):
    
#     orders = Order.objects.filter(user=request.user).order_by('order_date')
    
#     return render(request, 'Userside/order_history.html', {'orders': orders})
def order_history(request):
    status_filter = request.GET.get('status', 'All')
    all_statuses = ["All", "Pending", "Processing", "Shipped", "Delivered", "Cancelled", "Returned"]

    orders = Order.objects.filter(user=request.user)

    if status_filter != "All":
        orders = orders.filter(status=status_filter)

    context = {
        'orders': orders,
        'selected_status': status_filter,
        'all_statuses': all_statuses,
    }
    return render(request,'Userside/order_history.html', context)



from django.shortcuts import render, get_object_or_404
from .models import Order, OrderItem, OrderAddress
from django.contrib.auth.decorators import login_required

@login_required
def userorder_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    print(order)
    
    order_items = OrderItem.objects.filter(order_id=order_id)
    print(order_items)
   
    order_address = OrderAddress.objects.filter(order_id=order_id).first()
    print(order_address)
   
    for item in order_items:
        item.total_price = item.quantity * item.price

    context = {
        'order': order,
        'order_items': order_items,
        'order_address': order_address,
    }
    return render(request, 'Userside/Userorderdetails.html', context)


@login_required
def cancel_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status in ['Pending', 'Processing']:
            order.status = 'Cancelled'
            order.save()
            return JsonResponse({'status': 'success', 'message': 'Order cancelled successfully'}, status=200)
        else:
            return JsonResponse({'status': 'fail', 'message': 'Order cannot be cancelled at this stage'}, status=400)
    
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'}, status=405)

