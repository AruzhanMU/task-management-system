from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm, TaskForm, CommentForm
from django.contrib.auth.decorators import login_required
from .models import Task
from django.contrib import messages
from .utils import log_task_action
from django.db.models import Count
import csv
from django.http import HttpResponse
from weasyprint import HTML
from django.template.loader import render_to_string


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

    if request.user.role == 'admin':
        tasks = Task.objects.all()
    elif request.user.role == 'manager':
        tasks = Task.objects.filter(assigned_to__role='worker')
    else:
        tasks = Task.objects.filter(assigned_to=request.user)

    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # Добавим статистику
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
            task.save()
            messages.success(request, 'Task created successfully.')
            return redirect('dashboard')
    else:
        form = TaskForm()

    return render(request, 'tasks/task_create.html', {'form': form})

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    old_status = task.status  # до редактирования

    if request.user != task.created_by and request.user.role != 'admin':
        messages.error(request, 'You are not allowed to edit this task.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            updated_task = form.save()
            # логируем, если изменён статус
            if old_status != updated_task.status:
                log_task_action(task=updated_task, user=request.user,
                                action=f"Changed status from {old_status} to {updated_task.status}")
            messages.success(request, 'Task updated successfully.')
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/task_edit.html', {'form': form})

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


