from groq import Groq
from django.conf import settings


def ask_ai(user_text):
    try:
        if not settings.GROQ_API_KEY:
            return "Ошибка: API ключ не настроен"

        if not user_text or len(user_text.strip()) == 0:
            return "Пожалуйста, введите ваш вопрос"

        client = Groq(api_key=settings.GROQ_API_KEY)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "user", "content": user_text}
            ],
            max_tokens=1024,
        )

        return response.choices[0].message.content

    except Exception as e:
        if "429" in str(e):
            return "Лимит Groq API превышен. Попробуйте позже."

        return f"Ошибка при обращении к AI: {str(e)}"