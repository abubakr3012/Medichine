from twilio.rest import Client
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Appointment
import os


def send_sms(phone_number, message):
    
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        if phone_number.startswith('+'):
            phone_number = phone_number[1:]
        
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_SMS_FROM,
            to=f'+{phone_number}'
        )
        return message.sid
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None


def send_appointment_reminder(appointment):
    if not appointment.patient.phone:
        print(f"No phone number for patient {appointment.patient.username}")
        return None
    
    doctor_name = appointment.doctor.user.username
    appointment_time = appointment.date.strftime('%d.%m.%Y в %H:%M')
    
    message = (
        f"Напоминание: У вас есть запись к врачу {doctor_name} "
        f"на {appointment_time}. "
        f"Пожалуйста, будьте вовремя."
    )
    
    return send_sms(appointment.patient.phone, message)


def check_and_send_reminders():
    
    now = timezone.now()
    six_hours_later = now + timedelta(hours=6)
    
    # Ищем назначения в интервале от 6 часов до 6 часов + 1 минута
    # Только те, которым еще не отправлено напоминание
    appointments = Appointment.objects.filter(
        date__gte=six_hours_later,
        date__lte=six_hours_later + timedelta(minutes=1),
        status='approved',
        is_deleted=False,
        sms_reminder_sent=False
    ).select_related('patient', 'doctor__user')
    
    sent_count = 0
    for appointment in appointments:
        result = send_appointment_reminder(appointment)
        if result:
            # Отмечаем, что напоминание отправлено
            appointment.sms_reminder_sent = True
            appointment.save()
            sent_count += 1
            print(f"Sent reminder to {appointment.patient.username} for appointment at {appointment.date}")
    
    return sent_count
