from django import template

register = template.Library()


@register.filter
def completed_count(subtasks):
    """Возвращает количество выполненных подзадач."""
    return subtasks.filter(is_completed=True).count()