
from django.contrib.auth.decorators import login_required,permission_required
from django.shortcuts import render,redirect
from django.contrib.auth import login,logout,authenticate
from random import randint
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailConfirm,ResetPassword
from django.contrib.auth import get_user_model

User=get_user_model()


def send_confirmation_email(user):
    code=randint(100000,999999)
    EmailConfirm.objects.update_or_create(user=user,defaults={"code":code})

    try:
        send_mail(
            subject='Confirm your password',
            message=f'''
Hello mr(ms) {user.username}\n
Welcome to our Medichine
Please confirm your password {code}
''',
from_email=settings.DEFAULT_FROM_EMAIL,
recipient_list=[user.email])
    except Exception as e:
        print(e)

def register(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        password2=request.POST['password2']
        email=request.POST['email']
        phone=request.POST['phone']

        if password!=password2:
            return render(request,'accounts/register.html',{"error":'passwords are not match'})
        if User.objects.filter(phone=phone).exists():
            return render(request, 'accounts/register.html', {'error': 'This phone is already used'})
        elif User.objects.filter(username=username).exists():
            return render(request,'accounts/register.html',{'error':'this username is already taken'})
        elif User.objects.filter(email=email).exists():
            return render(request,'accounts/register.html',{'error':'this email is already taken'})

        user=User.objects.create_user(username=username,email=email,password=password,phone=phone)

        user.is_active=False
        user.save()
        send_confirmation_email(user)
        return render(request,'accounts/confirmation.html',{'username':user.username})
    else:
        return render(request,'accounts/register.html')
    
def login_user(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        
        user=authenticate(request,username=username,password=password)

        if not user:
            not_active=User.objects.filter(username=username,is_active=False).first()
            if not_active:
                return render(request,'accounts/login.html',{'error':'Please confirm your email'})
            else:
                return render(request,'accounts/login.html',{'error':'username or password is wrong'})
        else:
            login(request,user)
            return redirect('/redirect_dashboard/')
    else:
        return render(request,'accounts/login.html')

def logout_user(request):
    logout(request)
    return render(request,'accounts/login.html')

def confirm_email(request):
    if request.method=='POST':
        username=request.POST['username']
        code=request.POST['code']
        user=User.objects.filter(username=username).first()

        if not user:
            return render(request,'accounts/confirmation.html',{'error':'invalid username'})
        
        if user.is_active:
            return redirect('login')
        confirm=EmailConfirm.objects.filter(user=user,code=code).first()
        if not confirm:
            return render(request,'accounts/login.html',{'error':'Wrong code.Try again'})
        user.is_active=True
        user.save()
        confirm.delete()
        return redirect('login')
    else:
        return render(request,'accounts/confirmation.html')
    
def send_reset_code(user):
    code=randint(100000,999999)
    ResetPassword.objects.update_or_create(
        user=user,
        defaults={'code':code}
    )
    send_mail (
        subject='reset_password',
        message=f'Your reset code {code}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email]
    )


def forget_password(request):
    if request.method=='POST':
        email=request.POST['email']
        user=User.objects.filter(email=email).first()

        if not user:
            return render(request,'accounts/forget.html',{'error':'Email is not found'})
        send_reset_code(user)
        return render(request,'accounts/reset_confirm.html',{'email':email})
    return render(request,'accounts/forget.html')

def reset_confirm(request):
    if request.method == "POST":
        email = request.POST.get('email')
        code = request.POST.get('code')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            return render(request, 'accounts/reset_confirm.html', {
                'error': 'Passwords are not match',
                'email': email
            })

        user = User.objects.filter(email=email).first()

        if not user:
            return redirect('forget_password')

        confirm = ResetPassword.objects.filter(user=user, code=code).first()

        if not confirm:
            return render(request, 'accounts/reset_confirm.html', {
                'error': 'Wrong code. Try again',
                'email': email
            })

        user.set_password(password)
        user.save()

        ResetPassword.objects.filter(user=user).delete()

        return redirect('login')

    return redirect('forget_password')

@login_required
def redirect_dashboard(request):

    if request.user.role == 'doctor':
        return redirect('doctor_dashboard')

    elif request.user.role == 'patient':
        return redirect('patient_dashboard')

    elif request.user.role == 'admin':
        return redirect('admin_dashboard')

    return redirect('login')


@login_required
def patient_dashboard(request):

    return render(
        request,
        'dashboard/patient_dashboard.html',
        {
            'user': request.user
        }
    )


@login_required
def doctor_dashboard(request):

    return render(
        request,
        'dashboard/doctor_dashboard.html',
        {
            'user': request.user
        }
    )

@login_required
def admin_dashboard(request):

    return render(
        request,
        'dashboard/admin_dashboard.html',
        {
            'user': request.user
        }
    )