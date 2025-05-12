
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from Accountsapp.models import MyUser
from PIL import Image
import os
from  Categoryapp.models import Category
from  Productapp.models import  Product,ProductImage
from django.utils.text import slugify
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.core.files.base import ContentFile
from io import BytesIO

from django.core.exceptions import ValidationError

def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('Adminapp:admin_signin')
    return _wrapped_view


# Create your views here.
def is_admin(user):

    return user.is_authenticated and user.is_admin

#################################################
@admin_required
def admin_dashboard(request):
    categories = Category.objects.filter(is_deleted=False)
    # categories = Category.objects.all()  # Assuming you have a Category model
    # products = Product.objects.all() 
    
    context = {
        'categories': categories,
    }
    return render(request, 'Adminside/admindashboard.html', context)


   

   

################################

def admin_signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(request.POST)

        print(f"Email: {email}, Password: {password}")  # Logging

        if not email or not password:
            messages.error(request, "Both email and password are required.")
            return redirect('admin_signin')

        user = authenticate(request, email=email, password=password)

        if user is not None and user.is_admin:
            print(f"Authenticated admin: {user.email}")
            login(request, user)
            return redirect('Adminapp:admin_dashboard')
        else:
            print("Invalid credentials or not an admin")
            messages.error(request, "Invalid credentials or not authorized.")
            return redirect('Adminapp:admin_signin')
    return render(request, 'Adminside/admin_signin.html')


####################################
from django.contrib.auth import logout


def adminlogout(request):
    logout(request)
    return redirect('Adminapp:admin_signin')  


#################################################
@admin_required
def list_users(request):
    users = MyUser.objects.all()
    return render(request, 'Adminside/list_users.html', {'users': users})

###########################################################
@admin_required
def block_unblock_user(request, user_id):
    user = get_object_or_404(MyUser, id=user_id)
    user.is_blocked = not user.is_blocked  # Toggle block/unblock status
    user.save()
    return redirect('Adminapp:list_users')

###############################################
@admin_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST.get('description', '')
        slug = request.POST.get('slug', '')

        # Check if slug is empty, generate it from the name
        if not slug:
            slug = slugify(name)
        
        # Check if the category or slug already exists
        if Category.objects.filter(slug=slug).exists():
            messages.error(request, 'Category with this slug already exists.')
            return redirect('Adminapp:add_category')

        # Create the category
        category = Category(name=name, description=description, slug=slug)
        category.save()

        messages.success(request, 'Category added successfully!')
        return redirect('Adminapp:list_categories')

    return render(request, 'Adminside/add_category.html')



##################################################################




def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()  #to remove unwanted space
        description = request.POST.get('description', '').strip()

        if not name:
            messages.error(request, "Category name is required.")
            return render(request, 'Adminside/edit_category.html', {'category': category})

        # Check for duplicate category name, excluding the current category
        if Category.objects.filter(name=name).exclude(id=category_id).exists():
            messages.error(request, "A category with this name already exists.")
            return render(request, 'Adminside/edit_category.html', {'category': category})

        # Save the updated values
        category.name = name
        category.description = description
        category.save()

        messages.success(request, "Category updated successfully!")
        return redirect('Adminapp:list_categories')

    # GET request - render the form with existing data
    return render(request, 'Adminside/edit_category.html', {'category': category})



###########################################################
@admin_required
def soft_delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.is_deleted = True
    category.save()
    messages.success(request, "Category deleted successfully!")
    return redirect('Adminapp:list_categories')

#################################################
@admin_required
def list_categories(request):
    search_query = request.POST.get('search', '')  # Get search query (if any)
    
    # Filter categories based on search query
    categories = Category.objects.filter(name__icontains=search_query, is_deleted=False)

    return render(request, 'Adminside/list_categories.html', {
        'categories': categories,
        'search_query': search_query  # Pass search query back to template
    })




##################################################


@admin_required
def add_product(request):
    if request.method == 'POST':
        product_name = request.POST['product_name']
        description = request.POST['description']
        price = request.POST['price']
        stock = request.POST['stock'] 
        category_id = request.POST.get('category_id')

        # Ensure category exists
        try:
            category = Category.objects.get(id=category_id, is_deleted=False)
        except Category.DoesNotExist:
            messages.error(request, "Category does not exist.")
            return redirect('Adminapp:add_product')

        # Check if the product name already exists (excluding soft-deleted products)
        if Product.objects.filter(product_name=product_name, is_deleted=False).exists():
            messages.error(request, f"Product with name '{product_name}' already exists. Please choose a different name.")
            return redirect('Adminapp:add_product')

        # Create the product
        product = Product.objects.create(
            product_name=product_name,
            description=description,
            price=price,
            stock=stock, 
            category=category
        )

        # Handle multiple images
        if 'images' in request.FILES:
            for file in request.FILES.getlist('images'):
                try:
                    # Open the image and resize it
                    image = Image.open(file)
                    image = image.resize((300, 300))  # Resize to 300x300 pixels

                    # Determine the image format
                    mime_type_to_format = {
                        'image/jpeg': 'JPEG',
                        'image/png': 'PNG',
                    }
                    image_format = mime_type_to_format.get(file.content_type, 'JPEG')  # Default to JPEG

                    # Save the resized image to an in-memory file
                    image_io = BytesIO()
                    image.save(image_io, format=image_format)

                    # Create a Django file-like object and save it to the database
                    resized_image = ContentFile(image_io.getvalue(), name=file.name)
                    ProductImage.objects.create(product=product, image=resized_image)

                except ValidationError as e:
                    messages.error(request, f"Error with file '{file.name}': {str(e)}")
                except Exception as e:
                    messages.error(request, f"Unexpected error with file '{file.name}': {str(e)}")

        else:
            messages.warning(request, "No images were uploaded for the product.")

        messages.success(request, "Product added successfully!")
        return redirect('Adminapp:list_products')

    # Get all categories for the form
    categories = Category.objects.filter(is_deleted=False)
    return render(request, 'Adminside/add_product.html', {'categories': categories})

##########################################################

@admin_required
def delete_product(request, product_id):
    # Get the product or return a 404 if it doesn't exist
    product = get_object_or_404(Product, id=product_id)

    # Mark the product as deleted
    product.is_deleted = True
    product.save()

    # Optionally, delete the associated product images (if needed)
    product.images.all().delete()

    messages.success(request, "Product permanently deleted!")
    return redirect('Adminapp:list_products')




########################################
@admin_required
def list_products(request):
    search_query = request.GET.get('search', '')  # Get search query (if any) from GET request
    category_id = request.GET.get('category_id')  # Get selected category ID (if any) from GET request

    # Filter products based on search query and category
    if category_id:
        products = Product.objects.filter(
            product_name__icontains=search_query,
            category_id=category_id,
            is_deleted=False  # Only show non-deleted products
        )
    else:
        products = Product.objects.filter(
            product_name__icontains=search_query,
            is_deleted=False  # Only show non-deleted products
        )

    # Get all categories for the dropdown (ensure they are not deleted)
    categories = Category.objects.filter(is_deleted=False)

    return render(request, 'Adminside/list_products.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query,  # Pass search query back to template
        'selected_category': category_id  # Pass selected category to retain the selected option
    })



###############################################################33333
@admin_required
def edit_product(request, product_id):
    # Get the product or return a 404 if it doesn't exist
    product = get_object_or_404(Product, id=product_id, is_deleted=False)

    if request.method == 'POST':
        # Get the updated product details from the form
        product_name = request.POST['product_name']
        description = request.POST['description']
        price = request.POST['price']
        stock = request.POST['stock'] 
        category_id = request.POST.get('category_id')

        # Ensure category exists
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            messages.error(request, "Category does not exist.")
            return redirect('Adminapp:edit_product', product_id=product_id)

        # Update the product object
        product.product_name = product_name
        product.description = description
        product.price = price
        product.stock = stock
        product.category = category
        product.save()  # Save changes to the product

        # Handle new images if uploaded
        if 'images' in request.FILES:
            # Delete old images (optional, if replacing all images)
            product.images.all().delete()  # Use 'images' instead of 'productimage_set'

            for file in request.FILES.getlist('images'):
                image = Image.open(file)
                image = image.resize((300, 300))  # Resize the image
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'products'))
                filename = fs.save(file.name, file)  # Save image to media folder
                ProductImage.objects.create(product=product, image=os.path.join('products', filename))

        messages.success(request, "Product updated successfully!")
        return redirect('Adminapp:list_products')

    # Get categories for the dropdown
    categories = Category.objects.filter(is_deleted=False)

    # Get current product images using the 'images' related name
    product_images = product.images.all()

    return render(request, 'Adminside/edit_product.html', {
        'product': product,
        'categories': categories,
        'product_images': product_images,
    })

#########################################
from orderapp.models import Order,OrderAddress,OrderItem

def orderlist(request):
    search_query = request.GET.get('search', '')
   
    orders = Order.objects.select_related('user').order_by('-order_date')  # recent orders first

    context = {
        'orders': orders
    }
    return render(request, 'Adminside/orderlist.html', context)




def orderdetails(request,order_id):
    order = get_object_or_404(Order,id=order_id)
    orderItem=OrderItem.objects.filter(order=order)
    orderAddress=OrderAddress.objects.filter(order=order).first()
     
    for item in orderItem:
        item.total_price = item.quantity * item.price
    
    if request.method == "POST" :
        new_status= request.POST.get('status')
        if new_status in ['Pending','Shipped','Delivered','Canceled']:
            order.status = new_status
            order.save()
            messages.success(request, f"Order status updated to '{new_status}'.")
            return redirect('Adminapp:orderdetails', order_id=order.id)
        else:
            messages.error(request, "Invalid status selected.")

    context = {
          'order': order,
          'orderItem': orderItem,
          'orderAddress': orderAddress,
    }
 
    return render(request,'Adminside/orderdetail.html',context)

@admin_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status in dict(Order.STATUS_CHOICES).keys():
            order.status = new_status
            order.save()
            messages.success(request, 'Order status updated successfully!')
        else:
            messages.error(request, 'Invalid status selected.')

        return redirect('Adminapp:orderlist')  

    return redirect('Adminapp:orderdetails', order_id=order_id)
