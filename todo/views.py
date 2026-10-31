from django.db import transaction
from django.db.models import (
    Case,
    Count,
    ExpressionWrapper,
    F,
    FloatField,
    IntegerField,
    Q,
    Value,
    When,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from .forms import CategoryModelForm, SubtaskModelForm, TasksModelForm
from .models import Category, Subtask, Tasks


class TasksListView(ListView):
    """Список задач"""

    model = Tasks
    template_name = "todo/list.html"
    sort_fields = {
        "priority": "priority",
        "category": "category__name",
        "deadline": "due_date",
        "progress": "progress",
    }

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .annotate(
                subtask_total=Count("subtasks"),
                subtask_done=Count("subtasks", filter=Q(subtasks__is_done=True)),
                progress=Case(
                    When(subtask_total=0, then=Value(0.0)),
                    default=ExpressionWrapper(
                        F("subtask_done") * 100.0 / F("subtask_total"),
                        output_field=FloatField(),
                    ),
                    output_field=FloatField(),
                ),
                priority_order=Case(
                    When(priority="low", then=Value(0)),
                    When(priority="medium", then=Value(1)),
                    When(priority="high", then=Value(2)),
                    default=Value(1),
                    output_field=IntegerField(),
                ),
            )
        )
        return self._apply_sorting(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sort"] = self.request.GET.get("sort", "")
        context["order"] = self.request.GET.get("order", "asc")
        context["now"] = timezone.now()
        return context

    def _apply_sorting(self, queryset):
        sort = self.request.GET.get("sort")
        order = self.request.GET.get("order", "asc")
        if sort not in self.sort_fields or order not in ("asc", "desc"):
            return queryset
        descending = order == "desc"
        if sort == "priority":
            field = F("priority_order")
        elif sort == "category":
            field = F("category__name")
        elif sort == "deadline":
            field = F("due_date")
        else:
            field = F("progress")
        if sort in ("category", "deadline"):
            return queryset.order_by(
                field.desc(nulls_last=True) if descending else field.asc(nulls_last=True),
                "id",
            )
        return queryset.order_by(field.desc() if descending else field.asc(), "id")


class TasksActiveListView(TasksListView):
    """Список активных (невыполненных) задач"""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class TasksCreateView(CreateView):
    """Создание задачи"""

    template_name = "todo/create.html"
    form_class = TasksModelForm
    success_url = reverse_lazy("todo:index")


class TasksEditView(UpdateView):
    """Редактирование задачи"""

    model = Tasks
    template_name = "todo/edit.html"
    form_class = TasksModelForm
    success_url = reverse_lazy("todo:index")


class TasksDetailView(DetailView):
    """Страница задачи с подзадачами"""

    model = Tasks
    template_name = "todo/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subtask_form"] = SubtaskModelForm()
        return context


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


class SubtaskCreateView(View):
    """Добавление подзадачи"""

    @staticmethod
    def post(request, pk):
        task = get_object_or_404(Tasks, pk=pk)
        form = SubtaskModelForm(request.POST)
        if form.is_valid():
            Subtask.objects.create(task=task, **form.cleaned_data)
            return redirect("todo:detail", pk=task.pk)
        return render(request, "todo/detail.html", {
            "tasks": task,
            "subtask_form": form,
        })


class SubtaskToggleView(View):
    """Переключение статуса подзадачи"""

    @staticmethod
    def post(request, pk):
        with transaction.atomic():
            subtask = get_object_or_404(Subtask, pk=pk)
            subtask.is_done = not subtask.is_done
            subtask.save()
        return redirect("todo:detail", pk=subtask.task_id)


class SubtaskDeleteView(View):
    """Удаление подзадачи"""

    @staticmethod
    def get(request, pk):
        subtask = get_object_or_404(Subtask, pk=pk)
        return render(request, "todo/subtask_confirm_delete.html", {"subtask": subtask})

    @staticmethod
    def post(request, pk):
        subtask = get_object_or_404(Subtask, pk=pk)
        task_pk = subtask.task_id
        subtask.delete()
        return redirect("todo:detail", pk=task_pk)


class CategoryListView(ListView):
    """Список категорий"""

    model = Category
    template_name = "todo/category_list.html"


class CategoryCreateView(CreateView):
    """Создание категории"""

    template_name = "todo/category_form.html"
    form_class = CategoryModelForm
    success_url = reverse_lazy("todo:category_list")


class CategoryEditView(UpdateView):
    """Редактирование категории"""

    model = Category
    template_name = "todo/category_form.html"
    form_class = CategoryModelForm
    success_url = reverse_lazy("todo:category_list")


class CategoryDeleteView(DeleteView):
    """Удаление категории"""

    model = Category
    template_name = "todo/category_confirm_delete.html"
    success_url = reverse_lazy("todo:category_list")
