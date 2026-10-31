from django.db import models


class Category(models.Model):
    """Категория задачи"""

    name = models.CharField(max_length=100, verbose_name="Название")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Tasks(models.Model):
    """Задача"""

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Низкий"),
        (PRIORITY_MEDIUM, "Средний"),
        (PRIORITY_HIGH, "Высокий"),
    ]

    title = models.CharField(max_length=255, verbose_name="Наименование")
    is_active = models.BooleanField(verbose_name="Выполнена", default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    completed_at = models.DateTimeField(
        verbose_name="Время завершения", blank=True, null=True
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
        verbose_name="Приоритет",
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    deadline = models.DateTimeField(
        verbose_name="Дедлайн", blank=True, null=True
    )

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"


class Subtask(models.Model):
    """Подзадача"""

    task = models.ForeignKey(
        Tasks,
        verbose_name="Задача",
        on_delete=models.CASCADE,
        related_name="subtasks",
    )
    title = models.CharField(max_length=255, verbose_name="Наименование")
    is_completed = models.BooleanField(verbose_name="Выполнена", default=False)

    class Meta:
        verbose_name = "Подзадача"
        verbose_name_plural = "Подзадачи"

    def __str__(self):
        return self.title
