# appointments/signals.py

import logging
from datetime import timedelta

from celery import current_app
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from appointments.models import Appointment
from appointments.tasks import send_appointment_reminder

logger = logging.getLogger(__name__)

REMINDER_HOURS = getattr(settings, 'REMINDER_HOURS', [24, 12, 6])


def _schedule_reminders(appointment: Appointment):
    """Планирует напоминания за 24, 12 и 6 часов до приёма."""
    task_ids = []

    for hours in REMINDER_HOURS:
        send_at = appointment.date - timedelta(hours=hours)

        if send_at <= timezone.now():
            logger.info(
                f'Skipping {hours}h reminder for appointment {appointment.pk}: '
                f'send_at={send_at} already in the past.'
            )
            continue

        result = send_appointment_reminder.apply_async(
            args=[appointment.pk, hours],
            eta=send_at,
        )
        task_ids.append(result.id)
        logger.info(
            f'Scheduled {hours}h reminder for appointment {appointment.pk}, '
            f'task_id={result.id}, eta={send_at}'
        )

    # Сохраняем ID задач без вызова save() (чтобы не зациклить сигнал)
    Appointment.objects.filter(pk=appointment.pk).update(celery_task_ids=task_ids)


def _cancel_reminders(appointment: Appointment):
    """Отзывает все запланированные задачи Celery для записи."""
    for task_id in (appointment.celery_task_ids or []):
        current_app.control.revoke(task_id, terminate=True)
        logger.info(f'Revoked task {task_id} for appointment {appointment.pk}')

    Appointment.objects.filter(pk=appointment.pk).update(celery_task_ids=[])


@receiver(pre_save, sender=Appointment)
def handle_status_change(sender, instance, **kwargs):
    """
    Срабатывает при любом изменении записи.
    - Если статус изменился на 'cancelled' — отзываем задачи.
    - Если статус изменился с 'cancelled' на другой — перепланируем.
    - Если изменилась дата приёма — перепланируем.
    """
    if not instance.pk:
        return  # новая запись — обрабатываем в post_save

    try:
        old = Appointment.objects.get(pk=instance.pk)
    except Appointment.DoesNotExist:
        return

    status_cancelled = (old.status != 'cancelled' and instance.status == 'cancelled')
    status_restored  = (old.status == 'cancelled' and instance.status != 'cancelled')
    date_changed     = (old.date != instance.date)

    if status_cancelled:
        _cancel_reminders(old)

    elif status_restored or date_changed:
        # Отменяем старые задачи и перепланируем
        _cancel_reminders(old)
        # post_save перепланирует — передаём флаг через instance
        instance._reschedule = True


@receiver(post_save, sender=Appointment)
def handle_appointment_saved(sender, instance, created, **kwargs):
    """
    - При создании новой записи — планируем напоминания.
    - При восстановлении / изменении даты — перепланируем.
    """
    if created:
        _schedule_reminders(instance)
    elif getattr(instance, '_reschedule', False):
        _schedule_reminders(instance)
