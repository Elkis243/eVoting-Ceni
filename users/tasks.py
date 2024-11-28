from celery import shared_task
from django.core.mail import EmailMultiAlternatives
import pyotp
from django.conf import settings
import os
from django.core.management import call_command
from datetime import datetime

@shared_task
def send_otp(secretOtpKey, email):
    totp = pyotp.TOTP(secretOtpKey, interval=300)
    otp = totp.now()

    subject = "Ceni eVoting : Code de confirmation"
    message = f"Votre code de vérification est : {otp}\nCe code est valable pendant 5 minutes."

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=[email],
    )
    email_message.send()





    
    
@shared_task
def send_vote_evidence(vote_evidence, email):
    subject = "Ceni eVoting : Code de référence"
    message = f"Code de référence de votre bulletin dans l'urne: {vote_evidence}"

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=[email],
    )
    email_message.send()

@shared_task
def send_password(password, email):
    subject = "Ceni eVoting: Mot de passe"
    message = f"Mot de passe: {password}"

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=[email],
    )
    email_message.send()

@shared_task
def backup_database():
    backup_dir = os.path.join(settings.BASE_DIR, 'backup')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f'db_backup_{timestamp}.json'
    local_path = os.path.join(backup_dir, filename)

    call_command('dumpdata', output=local_path)

    return f'Backup created: {local_path}'