from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, View

from .forms import TasksModelForm
from .models import Tasks


class TasksListView(ListView):
    """Список задач"""

    model = Tasks
    template_name = "todo/list.html"


class TasksActiveListView(TasksListView):
    """Список активных (невыполненных) задач"""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class TasksCreateView(CreateView):
    """Создание задачи"""

    template_name = "todo/create.html"
    form_class = TasksModelForm
    success_url = reverse_lazy("todo:index")


class TasksUpdateIsDoneView(View):
    """Переключение статуса выполнения задачи"""

    @staticmethod
    def post(request, pk):
        with transaction.atomic():
            item = get_object_or_404(Tasks, pk=pk)
            if item.is_active:
                item.is_active = False
                item.completed_at = timezone.now()
            else:
                item.is_active = True
                item.completed_at = None
            item.save()
        return redirect("todo:index")


class TasksDeleteView(View):
    """Удаление задачи"""

    @staticmethod
    def get(request, pk):
        return render(request, "todo/delete.html", {
            "item": get_object_or_404(Tasks, pk=pk)
        })

    @staticmethod
    def post(request, pk):
        get_object_or_404(Tasks, pk=pk).delete()
        return redirect("todo:index")
