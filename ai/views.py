from django.shortcuts import render
from .ai import ask_ai, get_speciality
from doctors.models import DoctorProfile

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
                user_city = None
                if hasattr(request.user, 'doctorprofile'):
                    user_city = request.user.doctorprofile.city
                elif hasattr(request.user, 'patientprofile'):
                    user_city = request.user.patientprofile.city

                qs = DoctorProfile.objects.filter(
                    speciality__icontains=speciality
                )

                if user_city:
                    qs = qs.filter(city__icontains=user_city)

                doctors = qs[:5]  

    return render(request, "ai/chat.html", {
        "answer": answer,
        "error_message": error_message,
        "doctors": doctors,
    })