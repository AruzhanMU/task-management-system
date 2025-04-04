from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from .models import Task
from django.core.mail import send_mail

@shared_task
def send_deadline_reminders():
    now = timezone.now()
    target_time = now + timedelta(hours=24)

    tasks = Task.objects.filter(
        deadline__range=(target_time - timedelta(minutes=1), target_time),
        status__in=['new', 'in_progress'],
        reminder_sent=False
    )

    for task in tasks:
        message = f"Reminder: Task '{task.title}' is due in 24 hours (Deadline: {task.deadline.strftime('%d %b %Y %H:%M')})."
        print(message)

        # Отправка письма
        send_mail(
            subject="Task Reminder",
            message=message,
            from_email='admin@taskmanager.local',
            recipient_list=[task.assigned_to.email],
            fail_silently=True,
        )

        # Обновим статус отправки
        task.reminder_sent = True
        task.save()
