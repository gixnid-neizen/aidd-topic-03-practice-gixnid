from django import forms

from .models import Category, Subtask, Tasks


class TasksModelForm(forms.ModelForm):
    """Задача"""

    due_date = forms.DateTimeField(
        required=False,
        label="Срок выполнения",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
    )

    class Meta:
        model = Tasks
        fields = ["title", "priority", "category", "due_date"]


class CategoryModelForm(forms.ModelForm):
    """Категория"""

    class Meta:
        model = Category
        fields = ["name"]


class SubtaskModelForm(forms.ModelForm):
    """Подзадача"""

    class Meta:
        model = Subtask
        fields = ["title"]
