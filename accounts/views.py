from django.contrib.auth.decorators import login_required,permission_required
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,logout,authenticate
from random import randint
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailConfirm,ResetPassword,User,Profile
from django.contrib.auth import get_user_model
from ai.ai import ask_ai
from .forms import ProfileForm
User=get_user_model()

def send_code_email(user, code, subject, heading, intro, action_text):
    plain_message = (
        f"Hello, {user.username}.\n\n"
        f"{intro}\n\n"
        f"Your code: {code}\n\n"
        "If you did not request this email, you can safely ignore it.\n"
        "Medicine"
    )
    html_message = f"""
    <div style="margin:0;padding:32px;background:#eef6f7;font-family:Segoe UI,Arial,sans-serif;color:#17212b;">
      <div style="max-width:560px;margin:0 auto;background:#ffffff;border:1px solid #d9e7ea;border-radius:18px;overflow:hidden;box-shadow:0 18px 50px rgba(16,36,47,.12);">
        <div style="padding:26px 30px;background:linear-gradient(135deg,#0b8f8a,#056d70);color:#ffffff;">
          <div style="font-size:13px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;opacity:.9;">Medicine</div>
          <h1 style="margin:10px 0 0;font-size:26px;line-height:1.2;">{heading}</h1>
        </div>
        <div style="padding:30px;">
          <p style="margin:0 0 12px;font-size:16px;">Здравствуйте, <strong>{user.username}</strong>.</p>
          <p style="margin:0 0 22px;color:#667789;font-size:15px;line-height:1.6;">{intro}</p>
          <div style="margin:0 0 22px;padding:18px;border-radius:14px;background:#dff7f3;text-align:center;">
            <div style="margin-bottom:6px;color:#056d70;font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;">{action_text}</div>
            <div style="font-size:34px;font-weight:900;letter-spacing:.18em;color:#17212b;">{code}</div>
          </div>
          <p style="margin:0;color:#667789;font-size:13px;line-height:1.5;">Если вы не запрашивали это письмо, просто проигнорируйте его.</p>
        </div>
      </div>
    </div>
    """
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_confirmation_email(user):
    code=randint(100000,999999)
    EmailConfirm.objects.update_or_create(user=user,defaults={"code":code})

    try:
        send_code_email(
            user=user,
            code=code,
            subject="Medicine: код подтверждения email",
            heading="Подтвердите ваш email",
            intro="Добро пожаловать в Medicine. Используйте этот код, чтобы завершить регистрацию и активировать аккаунт.",
            action_text="Код подтверждения",
        )
    except Exception as e:
        print(e)

def register(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        password2=request.POST['password2']
        email=request.POST['email']
        phone=request.POST['phone']
        age=request.POST['age']
        city=request.POST['city']

        if password!=password2:
            return render(request,'accounts/register.html',{"error":'passwords are not match'})
        if len(password) < 8:
            return render(request,'accounts/register.html',{"error":'Password must be at least 8 characters'})
        if User.objects.filter(phone=phone).exists():
            return render(request, 'accounts/register.html', {'error': 'This phone is already used'})
        elif User.objects.filter(username=username).exists():
            return render(request,'accounts/register.html',{'error':'this username is already taken'})
        elif User.objects.filter(email=email).exists():
            return render(request,'accounts/register.html',{'error':'this email is already taken'})

        user=User.objects.create_user(username=username,email=email,password=password,phone=phone, role='patient',age=age,city=city)  

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
            return redirect('/dashboard/')
    else:
        return render(request,'accounts/login.html')

@login_required(login_url='login')
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
    send_code_email(
        user=user,
        code=code,
        subject="Medicine: код восстановления пароля",
        heading="Восстановление пароля",
        intro="Мы получили запрос на сброс пароля. Введите этот код на странице восстановления, чтобы задать новый пароль.",
        action_text="Код восстановления",
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
        if len(password) < 8:
            return render(request, 'accounts/reset_confirm.html', {
                'error': 'Password must be at least 8 characters',
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

@login_required(login_url='login')
def redirect_dashboard(request):

    if request.user.role == 'doctor':
        return redirect('doctor_dashboard')

    elif request.user.role == 'patient':
        return redirect('patient_dashboard')

    elif request.user.role == 'admin':
        return redirect('admin_dashboard')

    return redirect('login')


@login_required(login_url='login')
def patient_dashboard(request):
    answer = ""

    if request.method == "POST":
        symptom = request.POST.get("symptom")

        if symptom:
            answer = ask_ai(symptom)

    return render(
        request,
        'dashboard/patient_dashboard.html',
        {
            "answer": answer
        }
    )

@login_required(login_url='login')
def doctor_dashboard(request):

    return render(
        request,
        'dashboard/doctor_dashboard.html',
        {
            'user': request.user
        }
    )

@login_required(login_url='login')
def admin_dashboard(request):

    return render(
        request,
        'dashboard/admin_dashboard.html',
        {
            'user': request.user
        }
    )

@login_required(login_url='login')
def create_profile(request):
    if request.method=='POST':
        form=ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = request.user.profile
            profile.age = form.cleaned_data['age']
            profile.phone = form.cleaned_data['phone']
            profile.photo = form.cleaned_data['photo']
            profile.city = form.cleaned_data['city']

            profile.save()
            return redirect('/')
        else:
            return redirect('/')
    else:
        form=ProfileForm()
        return render(request,'accounts/profile_form.html',{"form":form})

@login_required(login_url='login')
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    return render(request, "accounts/my_profile.html", {
        "profile": profile
    })

@login_required(login_url='login')
def update_profile(request):
    profile = request.user.profile
    if request.method=='POST':
        form=ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile.age = form.cleaned_data['age']
            profile.phone = form.cleaned_data['phone']
            profile.photo = form.cleaned_data['photo']
            profile.city=form.cleaned_data['city']
            profile.save()
            return redirect('my_profile')
        else:
            return redirect('dashboard')
    else:
        form=ProfileForm(
            initial={
                'age':profile.age,
                'phone':profile.phone
            }
        )
        return render(request,'accounts/profile_form.html',{"form":form})