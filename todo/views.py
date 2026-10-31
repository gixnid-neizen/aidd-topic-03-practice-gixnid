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


class TasksActiveListView(ListView):
    """Список активных задач"""

    model = Tasks
    template_name = "todo/list.html"

    def get_queryset(self):
        return Tasks.objects.filter(is_active=True)


class TasksCreateView(CreateView):
    """Создание задачи"""

    template_name = "todo/create.html"
    form_class = TasksModelForm
    success_url = reverse_lazy("todo:index")


class TasksUpdateIsDoneView(View):
    """Редактирование статуса задачи"""

    @staticmethod
    def post(request, pk):
        item = get_object_or_404(Tasks, id=pk)
        if item.is_active:
            Tasks.objects.filter(id=pk).update(is_active=False, completed_at=timezone.now())
        else:
            Tasks.objects.filter(id=pk).update(is_active=True, completed_at=None)
        return redirect("todo:index")


class TasksDeleteView(View):
    """Удаление задачи"""

    @staticmethod
    def get(request, pk):
        item = get_object_or_404(Tasks, id=pk)
        return render(request, "todo/delete.html", {
            "item": item
        })

    @staticmethod
    def post(request, pk):
        Tasks.objects.filter(id=pk).delete()
        return redirect("todo:index")
