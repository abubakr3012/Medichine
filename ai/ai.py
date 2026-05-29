import google.generativeai as genai
from django.conf import settings

def ask_ai(user_text):
    try:
        if not settings.GEMINI_API_KEY:
            return " Ошибка: API ключ не настроен. Проверьте .env файл и переменную GEMINI_API_KEY"
        
        if not user_text or len(user_text.strip()) == 0:
            return " Пожалуйста, введите ваш вопрос"
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="Ты медицинский помощник. Помогай людям с информацией о здоровье. Не ставь диагноз. Если вопрос требует осмотра врача, посоветуй обратиться к профессионалу."
        )
        
        response = model.generate_content(user_text)
        return response.text

    except Exception as e:
        return f" Ошибка при обращении к AI: {str(e)}"