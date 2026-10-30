from django.contrib import admin

from .models import Tasks


@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at", "completed_at")
    search_fields = ("title",)
    fields = ("title", "is_active", "completed_at")
