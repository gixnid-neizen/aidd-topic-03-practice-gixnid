from django.urls import include, path

from .views import (
    SubtaskCreateView,
    SubtaskDeleteView,
    SubtaskUpdateIsDoneView,
    TasksActiveListView,
    TasksCategoryCreateView,
    TasksCreateView,
    TasksDeleteView,
    TasksListView,
    TasksUpdateView,
    TasksUpdateIsDoneView,
)

app_name = "todo"

urlpatterns = [
    path("", TasksListView.as_view(), name="index"),
    path("active", TasksActiveListView.as_view(), name="active"),
    path("create", TasksCreateView.as_view(), name="create"),
    path("update/<int:pk>", TasksUpdateIsDoneView.as_view(), name="update"),
    path("edit/<int:pk>", TasksUpdateView.as_view(), name="edit"),
    path("delete/<int:pk>", TasksDeleteView.as_view(), name="delete"),
    path("category/create", TasksCategoryCreateView.as_view(), name="category_create"),
    path(
        "task/<int:task_pk>/subtask/create",
        SubtaskCreateView.as_view(),
        name="subtask_create",
    ),
    path(
        "task/<int:task_pk>/subtask/<int:pk>/update",
        SubtaskUpdateIsDoneView.as_view(),
        name="subtask_update",
    ),
    path(
        "task/<int:task_pk>/subtask/<int:pk>/delete",
        SubtaskDeleteView.as_view(),
        name="subtask_delete",
    ),
]
