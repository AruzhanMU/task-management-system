from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Task, Comment, Group
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'password1', 'password2')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role')

class TaskForm(forms.ModelForm):
    # Добавляем поле для выбора группы, не связанное напрямую с моделью
    group_to_assign = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False, # Делаем необязательным на уровне формы
        label="Assign to Group", # Метка для отображения
        help_text="Select a group to assign the task to all its members. This overrides 'Assign to user'."
    )

    class Meta:
        model = Task
        # Убираем 'group_assigned' из полей модели, которые использует форма
        fields = ['title', 'description', 'deadline', 'assigned_to', 'priority', 'status', 'attachment']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поле 'assigned_to' необязательным на уровне формы
        self.fields['assigned_to'].required = False
        self.fields['assigned_to'].queryset = CustomUser.objects.filter(role__in=['worker', 'manager'])
        # self.fields['group_assigned'].queryset = Group.objects.all() # Эта строка больше не нужна

        # Переносим поле group_to_assign после assigned_to для логичного порядка
        current_fields = list(self.fields.keys())
        # Убедимся, что 'assigned_to' и 'group_to_assign' существуют перед перемещением
        if 'assigned_to' in current_fields and 'group_to_assign' in current_fields:
           assigned_to_index = current_fields.index('assigned_to')
           current_fields.insert(assigned_to_index + 1, current_fields.pop(current_fields.index('group_to_assign')))
           self.fields = {key: self.fields[key] for key in current_fields}


    # Добавляем валидацию
    def clean(self):
        cleaned_data = super().clean()
        assigned_to_user = cleaned_data.get('assigned_to')
        assigned_to_group = cleaned_data.get('group_to_assign')

        # Проверяем, что выбрано что-то одно: либо пользователь, либо группа
        if not assigned_to_user and not assigned_to_group:
            raise ValidationError("You must assign the task to either a user or a group.")

        # Проверяем, что не выбраны оба одновременно
        if assigned_to_user and assigned_to_group:
            raise ValidationError("You cannot assign the task to both a user and a group. Please choose one.")

        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write a comment...'})
        }

class GroupForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Group
        fields = ['name', 'members']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if user.role == 'manager':
                self.fields['members'].queryset = CustomUser.objects.filter(role='worker')
            else:  # admin
                self.fields['members'].queryset = CustomUser.objects.all()

