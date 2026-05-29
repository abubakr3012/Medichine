from django.shortcuts import render
from .ai import ask_ai


def ai_chat(request):
    answer = ""
    error_message = ""

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        
        if not text:
            error_message = "Пожалуйста, введите ваш вопрос"
        else:
            answer = ask_ai(text)

    return render(request, "ai/chat.html", {
        "answer": answer,
        "error_message": error_message
    })