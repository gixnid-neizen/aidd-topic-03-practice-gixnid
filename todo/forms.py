from django import forms

from .models import Category, Subtask, Tasks


class DateTimeLocalInput(forms.DateTimeInput):
    """Поле выбора даты и времени с календарём браузера."""

    input_type = "datetime-local"


class TasksModelForm(forms.ModelForm):
    """Задача"""

    class Meta:
        model = Tasks
        fields = ["title", "deadline", "priority", "category"]
        widgets = {
            "deadline": DateTimeLocalInput(
                format="%Y-%m-%dT%H:%M",
                attrs={"class": "form-control"},
            ),
        }


class SubtaskModelForm(forms.ModelForm):
    """Подзадача"""

    class Meta:
        model = Subtask
        fields = ["title"]


class CategoryModelForm(forms.ModelForm):
    """Категория"""

    class Meta:
        model = Category
        fields = ["name"]