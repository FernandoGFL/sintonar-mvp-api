from django.core import mail
from django.template.loader import render_to_string
from django.core import management

from celery import shared_task
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@shared_task(name="send_email")
def task_send_email(subject, to, template, data):
    logger.info("Sending email...")

    conexao = mail.get_connection()
    conexao.open()
    mensagem_html = render_to_string(template, data)

    email = mail.EmailMultiAlternatives(
        subject,
        to=[to],
        connection=conexao
    )

    email.attach_alternative(mensagem_html, "text/html")

    email.send()

    conexao.close()

    logger.info("Email sent")

    return True


@shared_task(name="backup_database")
def backup_database():
    logger.info("Backing up database...")

    management.call_command("dbbackup")

    logger.info("Database backed up")

    return True
