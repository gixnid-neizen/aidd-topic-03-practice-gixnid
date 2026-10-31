from django.db.models import Case, Count, F, FloatField, IntegerField, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, UpdateView, View

from .forms import CategoryModelForm, SubtaskModelForm, TasksModelForm
from .models import Category, Subtask, Tasks

ALLOWED_SORT_FIELDS = ["priority", "category", "title", "created_at", "deadline", "progress"]


def _toggle_dir(current_dir):
    return "asc" if current_dir == "desc" else "desc"


def _next_dir(request, field):
    current_sort = request.GET.get("sort")
    current_dir = request.GET.get("dir", "desc")
    if current_dir not in ("asc", "desc"):
        current_dir = "desc"
    if current_sort == field:
        return _toggle_dir(current_dir)
    return "desc"


class TasksListView(ListView):
    """Список задач"""

    model = Tasks
    template_name = "todo/list.html"

    def get_queryset(self):
        queryset = Tasks.objects.all()
        sort = self.request.GET.get("sort")
        direction = self.request.GET.get("dir", "desc")
        if direction not in ("asc", "desc"):
            direction = "desc"
        order = "" if direction == "asc" else "-"

        if sort == "priority":
            queryset = queryset.annotate(
                _priority_order=Case(
                    When(priority="low", then=Value(1)),
                    When(priority="medium", then=Value(2)),
                    When(priority="high", then=Value(3)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
            queryset = queryset.order_by(f"{order}_priority_order")
        elif sort == "category":
            order_field = F("category__name")
            queryset = queryset.order_by(
                order_field.asc(nulls_last=True)
                if direction == "asc"
                else order_field.desc(nulls_last=True)
            )
        elif sort == "deadline":
            order_field = F("deadline")
            queryset = queryset.order_by(
                order_field.asc(nulls_last=True)
                if direction == "asc"
                else order_field.desc(nulls_last=True)
            )
        elif sort == "progress":
            queryset = queryset.annotate(
                total=Count("subtasks"),
                completed=Count("subtasks", filter=Q(subtasks__is_completed=True)),
            ).annotate(
                progress_frac=Case(
                    When(total=0, then=Value(0.0)),
                    default=F("completed") * 1.0 / F("total"),
                    output_field=FloatField(),
                )
            )
            queryset = queryset.order_by(f"{order}progress_frac")
        elif sort in ALLOWED_SORT_FIELDS:
            queryset = queryset.order_by(f"{order}{sort}")
        else:
            queryset = queryset.order_by("-created_at")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for field in ALLOWED_SORT_FIELDS:
            context[f"dir_{field}"] = _next_dir(self.request, field)
        return context


class TasksActiveListView(TasksListView):
    """Список активных задач"""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


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


class TasksUpdateView(UpdateView):
    """Редактирование задачи"""

    model = Tasks
    form_class = TasksModelForm
    template_name = "todo/edit.html"
    success_url = reverse_lazy("todo:index")


class TasksCategoryCreateView(CreateView):
    """Создание категории"""

    model = Category
    form_class = CategoryModelForm
    template_name = "todo/category_form.html"
    success_url = reverse_lazy("todo:index")


class SubtaskCreateView(CreateView):
    """Создание подзадачи"""

    model = Subtask
    form_class = SubtaskModelForm
    template_name = "todo/subtask_form.html"

    def form_valid(self, form):
        form.instance.task = get_object_or_404(Tasks, id=self.kwargs["task_pk"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("todo:index")


class SubtaskUpdateIsDoneView(View):
    """Переключение статуса подзадачи"""

    @staticmethod
    def post(request, task_pk, pk):
        subtask = get_object_or_404(Subtask, id=pk, task_id=task_pk)
        subtask.is_completed = not subtask.is_completed
        subtask.save()
        return redirect("todo:index")


class SubtaskDeleteView(View):
    """Удаление подзадачи"""

    @staticmethod
    def post(request, task_pk, pk):
        subtask = get_object_or_404(Subtask, id=pk, task_id=task_pk)
        subtask.delete()
        return redirect("todo:index")
