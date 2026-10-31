from django.db import models


class Category(models.Model):
    """Категория задачи"""

    name = models.CharField(max_length=100, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Tasks(models.Model):
    """Задача"""

    PRIORITIES = [
        ("low", "Низкий"),
        ("medium", "Средний"),
        ("high", "Высокий"),
    ]

    title = models.CharField(max_length=255, verbose_name="Наименование")
    priority = models.CharField(
        max_length=10,
        choices=PRIORITIES,
        default="medium",
        verbose_name="Приоритет",
        db_index=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name="Категория",
        db_index=True,
    )
    due_date = models.DateTimeField(
        verbose_name="Срок выполнения", blank=True, null=True, db_index=True
    )
    is_active = models.BooleanField(verbose_name="Выполнена", default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    completed_at = models.DateTimeField(
        verbose_name="Время завершения", blank=True, null=True
    )

    def subtask_progress(self):
        """Прогресс «выполнено/всего (N%)» или None, если подзадач нет."""
        total = self.subtasks.count()
        if total == 0:
            return None
        done = self.subtasks.filter(is_done=True).count()
        return f"{done}/{total} ({round(done * 100 / total)}%)"

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"


class Subtask(models.Model):
    """Подзадача"""

    task = models.ForeignKey(
        Tasks, on_delete=models.CASCADE, related_name="subtasks", verbose_name="Задача"
    )
    title = models.CharField(max_length=255, verbose_name="Наименование")
    is_done = models.BooleanField(default=False, verbose_name="Выполнена")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    class Meta:
        verbose_name = "Подзадача"
        verbose_name_plural = "Подзадачи"

    def __str__(self):
        return self.title
