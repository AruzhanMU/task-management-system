from .models import TaskLog

def log_task_action(task, user, action):
    TaskLog.objects.create(task=task, user=user, action=action)
