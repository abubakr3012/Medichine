from openai import OpenAI
from django.conf import settings

def ask_ai(user_text):
    try:
        if not settings.GROQ_API_KEY:
            return " Ошибка: API ключ не настроен. Проверьте .env файл и переменную GROQ_API_KEY"
        
        if not user_text or len(user_text.strip()) == 0:
            return " Пожалуйста, введите ваш вопрос"
        
        client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=1024,
            messages=[
                {
                    "role": "system",          
                    "content": "Ты медицинский помощник. Помогай людям с информацией о здоровье. Не ставь диагноз. Если вопрос требует осмотра врача, посоветуй обратиться к профессионалу."
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        return f" Ошибка при обращении к AI: {str(e)}"