from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from .forms import CustomUserCreationForm, TaskForm, CommentForm, CustomUserChangeForm, GroupForm, CustomUser, Group
from django.contrib.auth.decorators import login_required
from .models import Task
from django.contrib import messages
from .utils import log_task_action
from django.db.models import Count, Q
import csv
from django.http import HttpResponse
from weasyprint import HTML
from django.template.loader import render_to_string
from .calendar_service import create_calendar_event
from django.contrib.auth.forms import SetPasswordForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'tasks/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')

    if request.user.role == 'admin':
        tasks = Task.objects.all()

    elif request.user.role == 'manager':
        tasks = Task.objects.filter(
            Q(assigned_to=request.user) |
            Q(created_by=request.user)
        )

    else:  # worker
        tasks = Task.objects.filter(
            Q(assigned_to=request.user) |
            Q(assigned_group__members=request.user)  # 👈 Задачи групп, в которых состоит пользователь
        ).distinct()

    if status_filter:
        tasks = tasks.filter(status=status_filter)

    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    total = tasks.count()
    new = tasks.filter(status='new').count()
    in_progress = tasks.filter(status='in_progress').count()
    done = tasks.filter(status='done').count()

    return render(request, 'tasks/dashboard.html', {
        'tasks': tasks,
        'total': total,
        'new': new,
        'in_progress': in_progress,
        'done': done,
    })

@login_required
def task_create(request):
    if request.user.role not in ['manager', 'admin']:
        messages.error(request, 'You are not allowed to create tasks.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user

            # 👉 Добавляем назначение группы
            group_id = request.POST.get('group')
            if group_id:
                from .models import Group  # если ещё не импортировал
                try:
                    group = Group.objects.get(id=group_id)
                    task.group_assigned = group
                except Group.DoesNotExist:
                    pass  # если вдруг группу удалили

            task.save()
            form.save_m2m()

            try:
                create_calendar_event(task)
            except Exception as e:
                print(f"Google Calendar error: {e}")

            messages.success(request, 'Task created successfully.')
            return redirect('dashboard')
    else:
        form = TaskForm()

    # 🛠 Передаём список всех групп в форму
    from .models import Group
    groups = Group.objects.all()

    return render(request, 'tasks/task_create.html', {
        'form': form,
        'groups': groups,
    })

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    old_status = task.status

    # Разрешаем доступ: автор, админ, или назначенный исполнитель
    is_executor = request.user.role == 'worker' and request.user == task.assigned_to

    if not (request.user == task.created_by or request.user.role == 'admin' or is_executor):
        messages.error(request, 'You are not allowed to edit this task.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)

        # Если это исполнитель, отключим валидацию остальных полей
        if is_executor:
            # принудительно подставим старые значения в поля, которые исполнитель не должен менять
            for field_name in ['title', 'description', 'deadline', 'assigned_to', 'priority', 'attachment']:
                form.fields[field_name].disabled = True

        if form.is_valid():
            updated_task = form.save(commit=False)

            # если исполнитель — разрешаем менять только статус
            if is_executor:
                updated_task.title = task.title
                updated_task.description = task.description
                updated_task.deadline = task.deadline
                updated_task.assigned_to = task.assigned_to
                updated_task.priority = task.priority
                updated_task.attachment = task.attachment

            updated_task.save()

            if old_status != updated_task.status:
                log_task_action(task=updated_task, user=request.user,
                                action=f"Changed status from {old_status} to {updated_task.status}")

            messages.success(request, 'Task updated successfully.')
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task)
        if is_executor:
            for field_name in ['title', 'description', 'deadline', 'assigned_to', 'priority', 'attachment']:
                form.fields[field_name].disabled = True

    return render(request, 'tasks/task_edit.html', {'form': form, 'task': task})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.user != task.created_by and request.user.role != 'admin':
        messages.error(request, 'You are not allowed to delete this task.')
        return redirect('dashboard')

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'The task has been deleted.')
        return redirect('dashboard')

    return render(request, 'tasks/task_delete_confirm.html', {'task': task})

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.user != task.assigned_to and request.user != task.created_by and request.user.role != 'admin':
        messages.error(request, "You don't have access to this task.")
        return redirect('dashboard')

    comments = task.comments.all().order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            return redirect('task_detail', pk=task.pk)
    else:
        form = CommentForm()

    return render(request, 'tasks/task_detail.html', {
        'task': task,
        'comments': comments,
        'form': form
    })

@login_required
def task_statistics(request):
    # Получаем количество задач по пользователям
    task_counts = Task.objects.filter(status='done').values('assigned_to').annotate(task_count=Count('id'))

    # Получаем количество задач по дням
    task_dates = Task.objects.filter(status='done').extra(select={'day': "date(deadline)"}).values('day').annotate(task_count=Count('id')).order_by('day')

    return render(request, 'tasks/task_statistics.html', {
        'task_counts': task_counts,
        'task_dates': task_dates,
    })

@login_required
def export_task_report(request):
    # Фильтруем задачи по выполненным и просроченным
    tasks = Task.objects.filter(status__in=['done', 'new'])

    # Создаём ответ в формате CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="task_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Title', 'Description', 'Priority', 'Status', 'Deadline', 'Assigned to'])

    for task in tasks:
        writer.writerow([task.title, task.description, task.get_priority_display(), task.get_status_display(),
                         task.deadline, task.assigned_to.username])

    return response

@login_required
def export_task_report_pdf(request):
    tasks = Task.objects.filter(status__in=['done', 'new'])

    # Генерируем HTML с данными
    html_string = render_to_string('tasks/task_report_pdf.html', {'tasks': tasks})

    # Преобразуем HTML в PDF
    pdf_file = HTML(string=html_string).write_pdf()

    # Создаём ответ с PDF-файлом
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="task_report.pdf"'
    return response

User = get_user_model()

@login_required
def users_list(request):
    users = CustomUser.objects.all()
    if request.user.role == 'admin':
        groups = Group.objects.all()
    else:  # Менеджер видит только свои группы
        groups = Group.objects.filter(created_by=request.user)
    return render(request, 'tasks/users_list.html', {'users': users, 'groups': groups})

@login_required
def user_create(request):
    if request.user.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully.")
            return redirect('users_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'tasks/user_form.html', {'form': form})

@login_required
def user_edit(request, pk):
    if request.user.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully.")
            return redirect('users_list')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'tasks/user_form.html', {'form': form})

@login_required
def user_delete(request, pk):
    if request.user.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    user = get_object_or_404(User, pk=pk)
    user.delete()
    messages.success(request, "User deleted.")
    return redirect('users_list')

@login_required
def set_user_password(request, user_id):
    if request.user.role != 'admin':
        return redirect('dashboard')

    user = get_object_or_404(get_user_model(), id=user_id)

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password changed successfully.')
            return redirect('users_list')
    else:
        form = SetPasswordForm(user)

    return render(request, 'tasks/set_user_password.html', {'form': form, 'user': user})

@login_required
def group_create(request):
    if request.user.role not in ['admin', 'manager']:
        return redirect('dashboard')

    if request.method == 'POST':
        form = GroupForm(request.POST, user=request.user)  # <-- передаем user
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            form.save_m2m()  # сохранить участников
            messages.success(request, 'Group created successfully.')
            return redirect('users_list')
    else:
        form = GroupForm(user=request.user)  # <-- передаем user

    return render(request, 'tasks/group_create.html', {'form': form})

@login_required
def groups_list(request):
    if request.user.role == 'admin':
        groups = Group.objects.all()
    else:  # manager
        groups = Group.objects.filter(created_by=request.user)

    return render(request, 'tasks/groups_list.html', {'groups': groups})

@login_required
def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk)

    if request.user.role == 'manager' and group.created_by != request.user:
        messages.error(request, 'You are not allowed to edit this group.')
        return redirect('users_list')

    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group, user=request.user)  # <-- передаем user
        if form.is_valid():
            form.save()
            messages.success(request, 'Group updated successfully.')
            return redirect('users_list')
    else:
        form = GroupForm(instance=group, user=request.user)  # <-- передаем user

    return render(request, 'tasks/group_edit.html', {'form': form, 'group': group})

@login_required
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)

    if request.user.role == 'manager' and group.created_by != request.user:
        messages.error(request, 'You are not allowed to delete this group.')
        return redirect('users_list')

    group.delete()
    messages.success(request, 'Group deleted successfully.')
    return redirect('users_list')
