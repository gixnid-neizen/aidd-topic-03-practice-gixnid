from django.contrib import admin

from .models import Category, Subtask, Tasks


class SubtaskInline(admin.TabularInline):
    model = Subtask
    extra = 1


@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "priority",
        "category",
        "due_date",
        "is_active",
        "created_at",
        "completed_at",
    )
    list_filter = ("priority", "category")
    search_fields = ("title",)
    fields = ("title", "priority", "category", "due_date", "is_active", "completed_at")
    inlines = [SubtaskInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
