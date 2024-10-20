
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from Accountsapp.models import MyUser
from PIL import Image
import os
from  Categoryapp.models import Category
from  Productapp.models import  Product,ProductImage

# Create your views here.
def is_admin(user):

    return user.is_authenticated and user.is_admin

#################################################
def admin_dashboard(request):
    categories = Category.objects.all()  # Assuming you have a Category model
    products = Product.objects.all()     # Assuming you have a Product model

    return render(request,'Adminside/admindashboard.html', {
        'categories': categories,
        'products': products,
    })

    
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

def list_users(request):
    users = MyUser.objects.all()
    return render(request, 'Adminside/list_users.html', {'users': users})

###########################################################

def block_unblock_user(request, user_id):
    user = get_object_or_404(MyUser, id=user_id)
    user.is_blocked = not user.is_blocked  # Toggle block/unblock status
    user.save()
    return redirect('list_users')

###############################################


from django.contrib import messages

def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        # Check if name is empty
        if not name:
            messages.error(request, "Category name is required.")
            return render(request, 'Adminside/add_category.html')

        # Check if category with the same name exists
        if Category.objects.filter(name=name).exists():
            messages.error(request, "Category with this name already exists.")
            return render(request, 'Adminside/add_category.html')

        # Create the category
        Category.objects.create(name=name, description=description)
        messages.success(request, "Category added successfully!")
        return redirect('category_list')

    return render(request, 'Adminside/add_category.html')


##################################################################

def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.name = request.POST['name']
        category.description = request.POST['description']
        category.save()
        return redirect('category_list')

    return render(request, 'Adminside/edit_category.html', {'category': category})

###########################################################

def soft_delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.is_deleted = True
    category.save()
    return redirect('category_list')

##################################################


import os
from PIL import Image
from django.conf import settings
from django.shortcuts import redirect, render
from django.core.files.storage import FileSystemStorage
from django.contrib import messages

def add_product(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        category_id = request.POST.get('category_id')

        # Ensure category exists
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            messages.error(request, "Category does not exist.")
            return redirect('add_product')

        # Create the product
        product = Product.objects.create(name=name, description=description, price=price, category=category)

        # Handle multiple images
        if 'images' in request.FILES:
            for file in request.FILES.getlist('images'):
                # Resize image
                image = Image.open(file)
                image = image.resize((300, 300))  # Resize the image
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'products'))
                filename = fs.save(file.name, file)  # Save image to media folder
                ProductImage.objects.create(product=product, image=os.path.join('products', filename))

        messages.success(request, "Product added successfully!")
        return redirect('product_list')

    categories = Category.objects.filter(is_deleted=False)
    return render(request, 'Adminside/add_product.html', {'categories': categories})

##########################################################

def soft_delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_deleted = True
    product.save()
    return redirect('product_list')


########################################



def list_products(request):
    search_query = request.POST.get('search', '')  # Get search query (if any)
    category_id = request.POST.get('category_id')  # Get selected category ID (if any)
    
    # Filter products based on search query and category
    if category_id:
        products = Product.objects.filter(name__icontains=search_query, category_id=category_id, is_deleted=False)
    else:
        products = Product.objects.filter(name__icontains=search_query, is_deleted=False)

    # Get all categories for the dropdown (ensure they are not deleted)
    categories = Category.objects.filter(is_deleted=False)

    return render(request, 'Adminside/list_products.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query,  # Pass search query back to template
        'selected_category': category_id  # Pass selected category to retain the selected option
    })


###############################################################33333


def list_categories(request):
    search_query = request.POST.get('search', '')  # Get search query (if any)
    
    # Filter categories based on search query
    categories = Category.objects.filter(name__icontains=search_query, is_deleted=False)

    return render(request, 'Adminside/list_categories.html', {
        'categories': categories,
        'search_query': search_query  # Pass search query back to template
    })

