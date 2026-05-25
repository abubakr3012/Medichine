from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def ask_ai(user_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты медицинский помощник. "
                        "Не ставь диагноз."
                    )
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI Error: {str(e)}"