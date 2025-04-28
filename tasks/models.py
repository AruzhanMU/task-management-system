from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('worker', 'Executor'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='worker')

    telegram_id = models.BigIntegerField(blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateTimeField()
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_tasks')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)  # ✅ Добавили сюда
    created_at = models.DateTimeField(auto_now_add=True)
    reminder_sent = models.BooleanField(default=False)
    group_assigned = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')

    def __str__(self):
        return self.title

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} on {self.task.title}"

class TaskLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} on {self.task.title}"

class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)
    members = models.ManyToManyField(CustomUser, related_name='custom_groups')  # <--- изменили!
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_groups')

    def __str__(self):
        return self.name