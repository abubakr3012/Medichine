from django.core.management.base import BaseCommand
from appointments.sms_utils import check_and_send_reminders


class Command(BaseCommand):
    help = 'Send SMS reminders for appointments 6 hours before'

    def handle(self, *args, **options):
        self.stdout.write('Checking for appointments in 6 hours...')
        
        sent_count = check_and_send_reminders()
        
        if sent_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully sent {sent_count} reminder(s)')
            )
        else:
            self.stdout.write('No reminders to send at this time.')
