from django.contrib import admin

from todo.models import Category, Subtask, Tasks


@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "priority", "category", "created_at", "completed_at", "deadline")
    search_fields = ("title",)
    fields = ("title", "is_active", "priority", "category", "completed_at", "deadline")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Subtask)
class SubtaskAdmin(admin.ModelAdmin):
    list_display = ("title", "task", "is_completed")
    search_fields = ("title",)
    list_filter = ("is_completed",)