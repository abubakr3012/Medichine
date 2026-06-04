# SMS Уведомления для Назначений

## Описание
Система автоматически отправляет SMS напоминания пациентам за 6 часов до их назначения к врачу.

## Требования
- Twilio аккаунт с настроенным SMS
- Настроенные переменные окружения в `.env` файле

## Настройка

### 1. Переменные окружения
Добавьте следующие переменные в ваш `.env` файл:
```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_SMS_FROM=+1234567890
```

### 2. Получение Twilio Credentials
1. Зарегистрируйтесь на https://www.twilio.com/
2. Получите Account SID и Auth Token из консоли
3. Получите номер телефона для отправки SMS

## Использование

### Ручной запуск команды
```bash
python manage.py send_appointment_reminders
```

### Автоматический запуск (Cron Job)

#### Linux/Mac (crontab)
Добавьте следующую строку в crontab (`crontab -e`):
```bash
*/10 * * * * cd /path/to/Medichine && python manage.py send_appointment_reminders
```

Это будет запускать команду каждые 10 минут.

#### Windows (Task Scheduler)
1. Откройте Task Scheduler
2. Создайте новую задачу
3. Установите триггер: "Daily" или "At startup"
4. Установите действие: "Start a program"
   - Program: `python`
   - Arguments: `manage.py send_appointment_reminders`
   - Start in: `C:\Users\user\Desktop\Medichine`

## Как это работает
1. Команда проверяет назначения, которые произойдут через 6 часов
2. Отправляет SMS пациентам с информацией:
   - Имя врача
   - Время назначения
3. Отмечает, что напоминание отправлено (чтобы не отправлять дубликаты)

## Тестирование
```bash
# Тестовая отправка SMS
python manage.py shell
```

```python
from appointments.sms_utils import send_sms
send_sms('+992003993162', 'Тестовое сообщение')
```

## Устранение проблем
- Убедитесь, что Twilio credentials правильные
- Проверьте, что у пациента есть номер телефона в профиле
- Проверьте логи на наличие ошибок
