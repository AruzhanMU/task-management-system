from telegram.ext import Updater, CommandHandler
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings")
django.setup()

from tasks.models import Task, CustomUser

def start(update, context):
    user_id = update.message.from_user.id
    update.message.reply_text(f"👋 Welcome to Task Manager Bot!\nYour Telegram ID is: {user_id}")

def my_tasks(update, context):
    user_telegram_id = update.message.from_user.id
    try:
        user = CustomUser.objects.get(telegram_id=user_telegram_id)
        tasks = Task.objects.filter(assigned_to=user)
        if tasks.exists():
            response = "\n".join([f"📌 {task.title} — {task.get_status_display()}" for task in tasks])
        else:
            response = "🎉 No tasks assigned."
    except CustomUser.DoesNotExist:
        response = "❌ You are not registered. Please contact the admin."
    update.message.reply_text(response)

updater = Updater("8053088019:AAF0T9JPTJPV75FWE2r_zQ2eHNe3S7FBaLA", use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("tasks", my_tasks))

updater.start_polling()
updater.idle()
