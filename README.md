# 🗂️ Task Management System

**A complete task and user management system built with Django, integrated with Google Calendar and Telegram for seamless task notifications and coordination.**

---

## 🚀 Features

### 👤 User Management
- Roles: **Admin**, **Manager**, **Executor**
- Registration, login, logout, password reset
- Admin dashboard for user creation and editing

### ✅ Task Management
- Create, assign, and filter tasks
- Add deadlines, priority levels, and attachments
- Status tracking: `New`, `In Progress`, `Done`
- Task edit and delete permissions by role

### 💬 Collaboration & Communication
- Comment system on tasks
- Task activity history logging (status changes, assignments, edits)
- Email + Telegram notifications

### 📆 Google Calendar Integration
- Tasks are automatically added to Google Calendar
- Auth via OAuth2 using your Google account

### 🤖 Telegram Bot Integration
- Link your Telegram with your account using `/start`
- Use `/tasks` to view assigned tasks
- Auto-message when task is assigned
- Inline buttons to update task status (coming soon)

---

## 🧑‍💻 Technologies Used

- **Backend:** Python, Django, Django ORM, Celery, Redis
- **Frontend:** HTML, CSS (Bootstrap/Tailwind), Django Templates
- **Database:** SQLite
- **Integrations:** Google Calendar API, Telegram Bot API

---

## 📦 Installation Guide

### ⚙️ Requirements
- Python 3.11+
- Virtualenv (recommended)

### 🔧 Setup Steps

```bash
# Clone the repository
$ git clone https://github.com/AruzhanMU/task-management-system.git
$ cd task-management-system

# Create virtual environment
$ python3 -m venv .venv
$ source .venv/bin/activate  # On Windows use .venv\Scripts\activate

# Install dependencies
$ pip install -r requirements.txt

# Run migrations
$ python manage.py migrate

# Create a superuser
$ python manage.py createsuperuser

# Run the server
$ python manage.py runserver
```

---

## 🔐 Google Calendar Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Google Calendar API
3. Create OAuth client ID (Desktop)
4. Download the JSON file and rename it to `credentials.json`
5. Place it in the project root
6. The first time you run calendar sync, it will prompt login and generate `token.json`

---

## 🤖 Telegram Bot Setup

1. Go to [@BotFather](https://t.me/BotFather)
2. Create a bot and copy the token
3. Save it in `telegram_bot.py`
4. Run the bot:

```bash
python telegram_bot.py
```

5. In Telegram:
   - Send `/start` to the bot to link your account
   - Send `/tasks` to view your tasks
   
---

## 👩‍💻 Author

**AruzhanMU**  
Made with <3 using Django, Google APIs and lots of motivation.

---

## 📄 License


This project is licensed under the MIT License - see the LICENSE file for details.

