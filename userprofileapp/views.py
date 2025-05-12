from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from Accountsapp.models import MyUser
from .models import UserAddress
from orderapp.models import Order

@login_required
def user_profile(request):
    user = request.user
    addresses = UserAddress.objects.filter(user=user)
    orders = Order.objects.filter(user=user).order_by('-order_date')
    return render(request, 'UserProfile/profile.html', {
        'user': user,
        'addresses': addresses,
        'orders': orders,
    })



@login_required
def manage_addresses(request):
    user = request.user
    addresses = UserAddress.objects.filter(user=user)

    if request.method == 'POST':
        
        address_id = request.POST.get('address_id')
        name=request.POST.get('name')
        address_line1 = request.POST.get('address_line1')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        phone_number = request.POST.get('phone_number')
        is_shipping_address = 'is_shipping_address' in request.POST

        if not address_line1 or not city or not state or not zip_code:
            messages.error(request, "All fields are required.")
            return redirect('userprofileapp:manage_addresses')

        if address_id:
            address = get_object_or_404(UserAddress, id=address_id, user=user)
            address.name=name
            address.address_line1 = address_line1
            address.city = city
            address.state = state
            address.zip_code = zip_code
            address.phone_number = phone_number
            address.is_shipping_address = is_shipping_address
            address.save()
            messages.success(request, "Address updated successfully.")
        else:
            UserAddress.objects.create(
                user=user,
                name=name,
                address_line1=address_line1,
                city=city,
                state=state,
                zip_code=zip_code,
                phone_number=phone_number,
                is_shipping_address=is_shipping_address
            )
            messages.success(request, "New address added successfully.")
        return redirect('userprofileapp:manage_addresses')

    address_id = request.GET.get('address_id')
    address_to_edit = None
    if address_id:
        address_to_edit = get_object_or_404(UserAddress, id=address_id, user=user)

    return render(request, 'UserProfile/manage_addresses.html', {
        'addresses': addresses,
        'address_to_edit': address_to_edit,
    })

from django.http import HttpResponse

@login_required
def delete_address(request, address_id):
    try:
        address = UserAddress.objects.get(id=address_id)
        if address.user != request.user:
            return HttpResponse("You are not allowed to delete this address", status=403)
        address.delete()
        messages.success(request, "Address deleted successfully.")
    except UserAddress.DoesNotExist:
        return HttpResponse("Address does not exist", status=404)

    return redirect('userprofileapp:manage_addresses')




@login_required
def edit_profile(request):
    user = request.user
    addresses = UserAddress.objects.filter(user=user, is_shipping_address=False)
    shipping_address = UserAddress.objects.filter(user=user, is_shipping_address=True).first()

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        for address in addresses:
            address.name = request.POST.get(f"address_{address.id}_name", address.name)
            address.address_line1 = request.POST.get(f"address_{address.id}_line1", address.address_line1)
            address.city = request.POST.get(f"address_{address.id}_city", address.city)
            address.state = request.POST.get(f"address_{address.id}_state", address.state)
            address.zip_code = request.POST.get(f"address_{address.id}_zip_code", address.zip_code)
            
            address.save()

        if request.POST.get('same_as_user_address') == 'on':
            if shipping_address:
                shipping_address.delete()
            if addresses.exists():
                first = addresses.first()
                UserAddress.objects.create(
                    user=user,
                    name=first.name,
                    address_line1=first.address_line1,
                    city=first.city,
                    state=first.state,
                    zip_code=first.zip_code,
                    is_shipping_address=True
                )
        # else:
        #     if not shipping_address:
        #         shipping_address = UserAddress(user=user, is_shipping_address=True)
        #     shipping_address.address_line1 = request.POST.get('shipping_address_line1', shipping_address.address_line1)
        #     shipping_address.city = request.POST.get('shipping_city', shipping_address.city)
        #     shipping_address.state = request.POST.get('shipping_state', shipping_address.state)
        #     shipping_address.zip_code = request.POST.get('shipping_zip_code', shipping_address.zip_code)
        #     shipping_address.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('userprofileapp:user_profile')

    return render(request, 'UserProfile/edit_profile.html', {
        'user': user,
        'addresses': addresses,
        'shipping_address': shipping_address,
    })


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully!")
            return redirect('userprofileapp:user_profile')
        else:
            messages.error(request, "Error updating your password.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'UserProfile/change_password.html', {'form': form})


@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'UserProfile/user_orders.html', {'orders': orders})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status not in ['Cancelled', 'Delivered']:
        order.status = 'Cancelled'
        order.save()
        messages.success(request, "Order cancelled successfully.")
    else:
        messages.error(request, "This order cannot be cancelled.")
    return redirect('userprofileapp:user_profile')
