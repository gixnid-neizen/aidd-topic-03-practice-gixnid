from django.urls import path

from .views import (
    CategoryCreateView,
    CategoryDeleteView,
    CategoryEditView,
    CategoryListView,
    SubtaskCreateView,
    SubtaskDeleteView,
    SubtaskToggleView,
    TasksActiveListView,
    TasksCreateView,
    TasksDeleteView,
    TasksDetailView,
    TasksEditView,
    TasksListView,
    TasksUpdateIsDoneView,
)

app_name = "todo"

urlpatterns = [
    path("", TasksListView.as_view(), name="index"),
    path("active", TasksActiveListView.as_view(), name="active"),
    path("create", TasksCreateView.as_view(), name="create"),
    path("edit/<int:pk>", TasksEditView.as_view(), name="edit"),
    path("update/<int:pk>", TasksUpdateIsDoneView.as_view(), name="update"),
    path("delete/<int:pk>", TasksDeleteView.as_view(), name="delete"),
    path("<int:pk>", TasksDetailView.as_view(), name="detail"),
    path("categories", CategoryListView.as_view(), name="category_list"),
    path("categories/create", CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit", CategoryEditView.as_view(), name="category_edit"),
    path("categories/<int:pk>/delete", CategoryDeleteView.as_view(), name="category_delete"),
    path("task/<int:pk>/subtasks/add", SubtaskCreateView.as_view(), name="subtask_add"),
    path("subtask/<int:pk>/toggle", SubtaskToggleView.as_view(), name="subtask_toggle"),
    path("subtask/<int:pk>/delete", SubtaskDeleteView.as_view(), name="subtask_delete"),
]
