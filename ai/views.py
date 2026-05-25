from django.shortcuts import render
from .ai import ask_ai


def ai_chat(request):
    answer = ""

    if request.method == "POST":
        text = request.POST.get("text")

        answer = ask_ai(text)

    return render(request, "ai/chat.html", {
        "answer": answer
    })