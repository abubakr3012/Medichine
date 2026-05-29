import google.generativeai as genai
from django.conf import settings
import warnings
import time

warnings.filterwarnings('ignore', category=FutureWarning)


def ask_ai(user_text):
    try:
        if not settings.GEMINI_API_KEY:
            return "Ошибка: API ключ не настроен"

        if not user_text or len(user_text.strip()) == 0:
            return "Пожалуйста, введите ваш вопрос"

        genai.configure(api_key=settings.GEMINI_API_KEY)

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash"
        )

        time.sleep(2)  # задержка 2 секунды

        response = model.generate_content(user_text)

        return response.text

    except Exception as e:
        if "429" in str(e):
            return "Лимит Gemini API превышен. Попробуйте позже."

        return f"Ошибка при обращении к AI: {str(e)}"