from django.db import models


class Tasks(models.Model):
    """Задача"""

    title = models.CharField(max_length=255, verbose_name="Наименование")
    is_active = models.BooleanField(verbose_name="Выполнена", default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    completed_at = models.DateTimeField(
        verbose_name="Время завершения", blank=True, null=True
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
