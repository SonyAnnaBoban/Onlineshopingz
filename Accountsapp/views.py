
from django.shortcuts import render, redirect,HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate,login
from django.utils import timezone
import random
from django.core.mail import EmailMultiAlternatives
from django.templatetags.static import static
from  django.urls import reverse
from django.db import IntegrityError
from datetime import datetime, timedelta
from .models import MyUser
from Productapp.models import Product,ProductImage  
from Categoryapp.models import  Category
from django.contrib.auth import logout

import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError




def home(request):
    category_id = request.GET.get('category_id')

    # Filter products by selected category or get all active products
    products = Product.objects.filter(is_deleted=False).prefetch_related('images')
    if category_id:
        products = products.filter(category_id=category_id)

    # Prepare products with images for display
    products_with_images = [
        {'product': product,
        'images': product.images.all(),
        'category_slug': product.category.slug, 
        }
        for product in products
    ]

    # Fetch all active categories
    categories = Category.objects.filter(is_deleted=False)

    context = {
        'products_with_images': products_with_images,
        'categories': categories,
        'selected_category': category_id,
    }

    # Add user-specific context for authenticated users
    if request.user.is_authenticated:
        display_name = request.user.email.split('@')[0]
        context['display_name'] = display_name
        template = 'index.html'
    else:
        template = 'home_logged_out.html'

    return render(request, template, context)


##################################################
def userlogout(request):
    logout(request)
    return redirect('Accountsapp:user_login')  





#########################################################################
from django.contrib.auth import get_user_model
def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        print("Login email:", email)
        print("Login password:", password)

        if not email or not password:
            messages.error(request, 'Enter both email and password.')
            return render(request, 'Userside/login.html')
        
        user = authenticate(request, email=email, password=password)
        print("Authenticated user:", user)
        
        if user.is_blocked:
                messages.error(request, "Your account is blocked. Please contact support.")
                return redirect('Accountsapp:user_login')

        elif user.is_active:
                request.session['User_id'] = user.id
                login(request,user)
                print("User authenticated:", request.user.email)
                return redirect('Accountsapp:home')
        else:
            messages.error(request, 'Your account is inactive.')
    else:
        messages.error(request, 'Invalid login details.')

    return render(request, 'Userside/login.html')


######################################################################



def Register(request):
    if request.method == 'POST':
        # Collect form data
        Fname = request.POST.get('firstname')
        Lname = request.POST.get('lastname')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        # Validate First Name
        if not Fname or len(Fname) < 4:
            messages.error(request, 'First name is required and must be at least 4 characters long.')
            return render(request, 'Userside/register.html', {'Fname': Fname, 'Lname': Lname, 'email': email})

        if not Fname.isalpha():
            messages.error(request, 'First name should not contain numbers or special characters.')
            return render(request, 'Userside/register.html', {'Fname': Fname, 'Lname': Lname, 'email': email})

        # Validate Last Name
        if not Lname or len(Lname) < 4:
            messages.error(request, 'Last name is required and must be at least 4 characters long.')
            return render(request, 'Userside/register.html', {'Fname': Fname, 'Lname': Lname, 'email': email})

        if not Lname.isalpha():
            messages.error(request, 'Last name should not contain numbers or special characters.')
            return render(request, 'Userside/register.html', {'Fname': Fname, 'Lname': Lname, 'email': email})

        # Validate Email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email or not re.match(email_pattern, email):
            messages.error(request, 'Please enter a valid email address (e.g., example@gmail.com).')
            return render(request, 'Userside/register.html', {'Fname': Fname, 'Lname': Lname, 'email': email})

        # Check if passwords match
        if pass1 != pass2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'Userside/register.html', {'Fname': Fname, 'Lname': Lname, 'email': email})

        # Check if email already exists
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return render(request, 'Userside/register.html', {'Fname': Fname, 'Lname': Lname, 'email': email})

        # Generate OTP and send email
        otp = random.randint(100000, 999999)
        image_url = static('UserSide/img/mymail.jpeg')
        subject = 'Greetings from PlanterDream'
        from_email = 'izzatezza1922@gmail.com'
        to_email = [email]
        text_content = f'Your Registration OTP Code is {otp}'
        html_content = f'''
            <html>
                <body>
                    <h1>Welcome to PlanterDream!</h1>
                    <h5>The Right Time to Purchase your Dream Plant</h5>
                    <h4>Your Registration OTP Code is: <strong>{otp}</strong></h4>
                    <h4>Thank You For Choosing Us</h4>
                    <img src="{image_url}" alt="Company Logo" />
                </body>
            </html>
        '''
        
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        # Save registration details and OTP in session
        messages.success(request, 'OTP has been sent to your email. Please verify to complete registration.')
        request.session.update({
            'otp': str(otp),
            'time': timezone.now().isoformat(),
            'Fname': Fname,
            'Lname': Lname,
            'email': email,
            'pass1': pass1
        })

        return render(request, 'Userside/verify_otp.html')

    return render(request, 'Userside/register.html')


##################################################################

def resend_otp(request):
    otp_generation_time_str = request.session.get('time')
    
    if otp_generation_time_str:
        try:
            otp_generation_time = datetime.fromisoformat(otp_generation_time_str)
            otp_generation_time = timezone.make_aware(otp_generation_time, timezone.get_current_timezone())
        except ValueError:
            otp_generation_time = datetime.strptime(otp_generation_time_str, '%Y-%m-%d %H:%M:%S')
            otp_generation_time = timezone.make_aware(otp_generation_time, timezone.get_current_timezone())

        current_time = timezone.now()
        time_difference = current_time - otp_generation_time

        # Prevent sending another OTP if less than 60 seconds have passed
        if time_difference.total_seconds() < 60:
            messages.error(request, 'You can request a new OTP after 1 minute.')
            return render(request, 'Userside/verify_otp.html')

    # Generate a new OTP
    otp = random.randint(100000, 999999)
    print(f"New OTP: {otp}")  # For debugging

    # Prepare email content
    image_url = static('UserSide/img/mymail.jpeg')
    subject = 'Greetings from PlanterDream - Resend OTP'
    from_email = 'izzatezza1922@gmail.com'
    to_email = [request.session.get('email')]
    text_content = f'Your new OTP Code is {otp}'
    html_content = f'''
        <html>
            <body>
                <h1>Welcome to PlanterDream</h1>
                <h5>The Right Time To Purchase Your Dream Plant</h5>
                <h4>Your new OTP Code is: <strong>{otp}</strong></h4>
                <h4>Thank You For Choosing Us</h4>
                <img src="{image_url}" alt="Company Logo">
            </body>
        </html>
    '''

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        messages.success(request, 'OTP has been sent to your email.')
    except Exception as e:
        messages.error(request, f'Error occurred while sending email: {str(e)}')
        return render(request, 'Userside/verify_otp.html')

    # Store the new OTP and current time in the session
    request.session['otp'] = str(otp)
    request.session['time'] = timezone.now().isoformat()

    return render(request, 'Userside/verify_otp.html')



###################################################################################


def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        otp_generation_time_str = request.session.get('time')

        # Check if session data exists
        if otp_generation_time_str is None:
            messages.error(request, "Session expired. Please try again.")
            return redirect('Accountsapp:resend_otp')  # Redirect to resend OTP page

        # Parse OTP generation time
        try:
            otp_generation_time = datetime.fromisoformat(otp_generation_time_str)
        except ValueError:
            messages.error(request, "Invalid time format. Please try again.")
            return redirect('Accountsapp:resend_otp')

        # Check OTP expiration
        current_time = timezone.now()
        time_difference = current_time - otp_generation_time
        if time_difference > timedelta(minutes=10):
            messages.error(request, "OTP has expired. Please request a new one.")
            return redirect('Accountsapp:resend_otp')

        # Verify OTP
        if entered_otp == request.session.get('otp'):
            fname = request.session.get('Fname')
            lname = request.session.get('Lname')
            email = request.session.get('email')
            password = request.session.get('pass1')

            # Check if email is already registered
            if MyUser.objects.filter(email=email).exists():
                messages.error(request, "This email is already registered. Please use a different email.")
                return redirect('Accountsapp:Register')

            try:
                # Create the new user
                User = MyUser.objects.create_user(email=email, password=password, first_name=fname, last_name=lname)
                User.is_active = True
                User.save()

                # Clear session data after successful registration
                request.session.clear()

                messages.success(request, "Your account has been successfully created. You can now log in.")
                return redirect('Accountsapp:user_login')
            except IntegrityError:
                messages.error(request, "An error occurred during registration. Please try again.")
                return redirect('Accountsapp:Register')

        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('Accountsapp:verify_otp')  # Redirect to allow re-entry of OTP

    return redirect('Accountsapp:home')




