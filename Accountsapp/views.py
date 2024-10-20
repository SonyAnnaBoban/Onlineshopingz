
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
#from Adminapp.views import admin_dashboard
from .models import MyUser



def home(request):
    return render(request, 'index.html')  

def user_login(request):
        
    if request.method == "POST":

        email = request.POST.get('email')
        password = request.POST.get('password')
        # print("b4condtn",email,password)
        if not email or not password:
            print("aftercondtn",email,password)
            messages.error(request, 'Enter email and password')
            return render(request, 'Userside/login.html')
        
        User = authenticate(username=email,password=password)
        print("user",User)
        if User:
            print("User",User)
            if User.is_active:
                print(User.is_active, User.is_admin)
                # Check User permissions
                if User.is_admin:
                    # User is an admin
                    request.session['User_id'] = User.id
                    login(request, User)
                   # return HttpResponse('admin entered')
                    return redirect('Adminapp:admin_dashboard')
                else:
                    # User is a regular User
                    print(request.session.keys())   
                    request.session['User_id'] = User.id
                    login(request, User)
                    return redirect('home')
            else:
                print('not activated')
                messages.error(request, 'Your account is inactive.')
        else:
            print('not authenticated')
            messages.error(request, 'Invalid login details supplied.')
    
    return render(request, 'Userside/login.html')





def Register(request):
    if request.method == 'POST':
        Fname = request.POST.get('firstname')
        Lname = request.POST.get('lastname')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        # Password match validation
        if pass1 != pass2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')

        User = get_user_model()

        # Check if the email is already registered
        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return render(request, 'Userside/register.html')

        # Generate OTP
        otp = random.randint(100000, 999999)
        print("otp",otp)  # You can remove this in production

        # Email content
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
        
        # Sending the email
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        # OTP and User details stored in session
        messages.success(request, 'OTP has been sent to your email. Please verify to complete registration.')
        request.session['otp'] = str(otp)
        request.session['time'] = timezone.now().isoformat()
        request.session['Fname'] = Fname
        request.session['Lname'] = Lname
        request.session['email'] = email
        request.session['pass1'] = pass1

        return render(request, 'Userside/verify_otp.html')

    else:
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

        if otp_generation_time_str is None:
            messages.error(request, "Session expired. Please try again.")
            return render(request, 'Userside/verify_otp.html')

        try:
            otp_generation_time = datetime.fromisoformat(otp_generation_time_str)
        except ValueError:
            messages.error(request, "Invalid time format. Please try again.")
            return render(request, 'Userside/verify_otp.html')

        current_time = timezone.now()
        time_difference = current_time - otp_generation_time

        if time_difference > timedelta(seconds=600):
            messages.error(request, "OTP has expired. Please request a new one.")
            return render(request, 'Userside/verify_otp.html')

        if entered_otp == request.session.get('otp'):
            print("enteredotp", entered_otp)
            fname = request.session.get('Fname')
            lname = request.session.get('Lname')
            email = request.session.get('email')
            password = request.session.get('pass1')

            #User = get_user_model()

            if MyUser.objects.filter(email=email).exists():
                messages.error(request, "This email is already registered. Please use a different email.")
                return redirect('Accountsapp:Register')

            try:
                User = MyUser.objects.create_user(email=email,password=password, first_name=fname, last_name=lname)
                User.is_active = True
                User.save()

                request.session.clear()

                messages.success(request, "Your account has been successfully created. You can now log in.")
                return redirect('Accountsapp:user_login')
            except IntegrityError:
                messages.error(request, "An error occurred during registration. Please try again.")
                return redirect('Accountsapp:Register')

        else:
            messages.error(request, "Failed to verify OTP. Please try again.")
            return render(request, 'Userside/verify_otp.html')

    return redirect('Accountsapp:home')
