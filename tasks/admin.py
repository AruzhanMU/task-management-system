from django.contrib import admin
from .models import CustomUser, Task, Group
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'telegram_id', 'is_staff']

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'telegram_id')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'telegram_id')}),
    )

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'status', 'priority', 'deadline')
    list_filter = ('status', 'priority', 'deadline')
    search_fields = ('title', 'description')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Group)
