# Task Management System

This is a web-based **Task Management System** built with **Django**, designed to help users create, assign, track, and manage tasks with various statuses, priorities, and deadlines. The system supports role-based access control, where users can be assigned different roles: **Admin**, **Manager**, or **User**.

## Features
- **User Registration and Management**: Users can register, log in, and reset passwords.
- **Role-based Access**: Admin, Manager, and User roles with different levels of access.
- **Task Management**: Create, assign, and track tasks.
- **Task Filtering**: Filter tasks by status (New, In Progress, Done).
- **File Attachments**: Attach files to tasks.
- **Comments and Task History**: Add comments to tasks and track their history (status changes, user actions).
- **Email Notifications**: Notify users about task assignments and deadlines.

## Tech Stack
- **Backend**: Django (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS 
- **Others**: Python, Git, GitHub

## Installation

### Prerequisites:
- Python 3.x
- pip (Python package installer)

### Steps to Run the Project Locally:
1. **Clone the repository**:
   ```bash
   git clone https://github.com/AruzhanMU/task-management-system.git
   ```

2. **Navigate to the project directory**:
   ```bash
   cd task-management-system
   ```

3. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   ```

4. **Activate the virtual environment**:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

6. **Setup database and migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create a superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the server**:
   ```bash
   python manage.py runserver
   ```

9. **Access the application**:  
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

### Accessing the Admin Panel:
- Visit: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
- Use the superuser credentials to log in.

## Usage

Once the project is running, you can:
- **Log in** with your registered credentials.
- **Create tasks**, assign them to users, and track their progress.
- **Admin users** can manage users, assign roles, and view all tasks.
- **Comment on tasks** and view their history of changes.
- **View task details**, including priorities, deadlines, and attachments.

## Acknowledgements

- This project was built using Django, a high-level Python web framework.
- Thanks to all contributors for their valuable input.
