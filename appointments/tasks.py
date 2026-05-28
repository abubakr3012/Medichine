# appointments/tasks.py

import logging
from celery import shared_task
from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)


def _get_twilio_client() -> Client:
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def _build_message(patient_name: str, doctor_name: str, speciality: str, date, hours_before: int) -> str:
    time_str = date.strftime('%d.%m.%Y в %H:%M')

    if hours_before == 24:
        time_label = 'завтра'
    elif hours_before == 12:
        time_label = 'через 12 часов'
    else:
        time_label = 'через 6 часов'

    return (
        f"Здравствуйте, {patient_name}!\n"
        f"Напоминаем: {time_label} ({time_str}) у вас запись "
        f"к врачу {doctor_name} ({speciality}).\n"
        f"Если нужно отменить — сделайте это заранее в приложении."
    )


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_appointment_reminder(self, appointment_id: int, hours_before: int):
    from appointments.models import Appointment  # avoid circular import

    try:
        appt = (
            Appointment.objects
            .select_related('patient', 'doctor__user')
            .get(pk=appointment_id)
        )
    except Appointment.DoesNotExist:
        logger.warning(f'Appointment {appointment_id} not found, skipping.')
        return

    # Отправляем только если статус не отменён
    if appt.status == 'cancelled':
        logger.info(f'Appointment {appointment_id} is cancelled, skipping.')
        return

    # Берём телефон из Profile пациента (там актуальный номер)
    try:
        phone = appt.patient.profile.phone
    except Exception:
        phone = appt.patient.phone  # fallback на поле User

    if not phone:
        logger.error(f'No phone for patient {appt.patient.username}, skipping.')
        return

    message_body = _build_message(
        patient_name=appt.patient.get_full_name() or appt.patient.username,
        doctor_name=appt.doctor.user.get_full_name() or appt.doctor.user.username,
        speciality=appt.doctor.speciality,
        date=appt.date,
        hours_before=hours_before,
    )

    client = _get_twilio_client()
    errors = []

    # --- SMS ---
    try:
        sms = client.messages.create(
            to=phone,
            from_=settings.TWILIO_SMS_FROM,
            body=message_body,
        )
        logger.info(f'SMS sent to {phone}, SID={sms.sid}')
    except TwilioRestException as e:
        logger.error(f'SMS error for appointment {appointment_id}: {e}')
        errors.append(f'SMS: {e}')

    # --- WhatsApp ---
    try:
        wa = client.messages.create(
            to=f'whatsapp:{phone}',
            from_=settings.TWILIO_WA_FROM,
            body=message_body,
        )
        logger.info(f'WhatsApp sent to {phone}, SID={wa.sid}')
    except TwilioRestException as e:
        logger.error(f'WhatsApp error for appointment {appointment_id}: {e}')
        errors.append(f'WhatsApp: {e}')

    # Если оба канала упали — ретрай
    if len(errors) == 2:
        raise self.retry(exc=Exception('; '.join(errors)))
