from django.shortcuts import render
from .ai import ask_ai, get_speciality
from doctors.models import DoctorProfile
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def ai_chat(request):
    answer = ""
    error_message = ""
    doctors = []

    if request.method == "POST":
        text = request.POST.get("text", "").strip()

        if not text:
            error_message = "Пожалуйста, введите ваш вопрос"
        else:
            answer = ask_ai(text)
            speciality = get_speciality(text)

            if speciality:
                qs = DoctorProfile.objects.filter(speciality__icontains=speciality)

                # Берём город из профиля пользователя автоматически
                if request.user.is_authenticated:
                    try:
                        user_city = request.user.profile.city
                        if user_city:
                            qs = qs.filter(city__icontains=user_city)
                    except Exception:
                        pass

                doctors = qs[:5]

    return render(request, "ai/chat.html", {
        "answer": answer,
        "error_message": error_message,
        "doctors": doctors,
    })