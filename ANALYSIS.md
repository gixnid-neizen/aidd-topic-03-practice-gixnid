# ANALYSIS — Анализ проекта ToDo (Python/Django)

> **Исходный репозиторий:** `/home/default/projects/todo-Cline`  
> **Статус:** только чтение, без изменений  
> **Язык документации проекта:** русский

---

## 1) Назначение приложения и технологический стек

### Назначение
Приложение — классический **ToDo-менеджер** (список дел). Пользователь может:
- просматривать список задач (все или только активные);
- создавать новые задачи;
- переключать статус задачи «выполнена/не выполнена» (toggle);
- удалять задачи.

Проект используется в рамках практического занятия по AI Coding Agents (файл `PRACTICE.md`): студенты исследуют чужой код, восстанавливают требования, рефакторят и дорабатывают приложение.

### Технологический стек

| Компонент | Технология / версия | Источник |
|-----------|---------------------|----------|
| Язык программирования | Python 3 | `requirements.txt`, `.venv` |
| Веб-фреймворк | **Django == 4.1.7** | `requirements.txt` |
| База данных | **SQLite 3** (`django.db.backends.sqlite3`) | `config/settings.py:66-68` |
| ORM | Django ORM | `todo/models.py` |
| Шаблонизатор | Django Templates | `todo/templates/`, `config/settings.py:46-60` |
| CSS-фреймворк (UI) | **Bootstrap 3** (через `bootstrap.min.css`, `crispy_bootstrap3`) | `todo/static/todo/css/bootstrap.min.css`, `config/settings.py:26` |
| Формы | `django-crispy-forms == 2.0`, `crispy-bootstrap3` | `requirements.txt`, `todo/forms.py`, `todo/templates/todo/create.html` |
| Фильтрация | `django-filter == 22.1` (`django_filters`) | `requirements.txt`, `config/settings.py:22,31` |
| REST API (подключён, но не используется в Views) | `djangorestframework == 3.14.0` | `requirements.txt`, `config/settings.py:28-32` |
| JS-библиотеки (CDN) | jQuery 3.3.1 slim, Popper.js 1.14.6, Moment.js 2.23.0, Tempus Dominus Bootstrap 4, Font Awesome 4.7.0 | `todo/templates/todo/base.html:12-23` |
| ASGI / WSGI | встроенные в Django | `config/wsgi.py`, `config/asgi.py` |
| Dev-зависимости | `black == 23.1.0`, `isort == 5.12.0`, `mypy-extensions`, `click` и др. | `requirements.txt` |

Язык и локаль: **ru-RU**, часовой пояс **Europe/Moscow** (`config/settings.py:87-89`).
---

## 2) Структура проекта и назначение каждого каталога и ключевого файла

```
todo-Cline/
├── .gitignore                 # Исключения для Git
├── README.md                  # Инструкция по установке и запуску
├── PRACTICE.md                # Описание практического задания
├── requirements.txt           # Зависимости с версиями
├── manage.py                  # CLI точка входа Django
├── config/                    # Конфигурация проекта
│   ├── asgi.py                # ASGI точка входа
│   ├── settings.py            # Основные настройки (INSTALLED_APPS, DATABASES, TEMPLATES, MIDDLEWARE)
│   ├── urls.py                # Корневой URL-роутер
│   └── wsgi.py                # WSGI точка входа
├── todo/                      # Приложение todo
│   ├── admin.py               # Регистрация Tasks в админке
│   ├── apps.py                # Конфиг приложения TodoConfig
│   ├── forms.py               # TasksModelForm
│   ├── models.py              # Модель Tasks
│   ├── urls.py                # URL-роутер приложения
│   ├── views.py               # Классовые представления
│   ├── migrations/            # Миграции БД
│   ├── static/todo/css/       # CSS файлы
│   └── templates/todo/        # HTML шаблоны
└── db.sqlite3                 # SQLite база (в .gitignore)
```

| Файл | Назначение |
|------|------------|
| `manage.py` | Запуск команд Django |
| `config/settings.py` | Конфигурация приложений, БД, шаблонов, middleware |
| `config/urls.py` | Корневой роутер: admin + todo.urls |
| `todo/models.py` | Модель Tasks (ORM) |
| `todo/admin.py` | Настройка отображения в админке |
| `todo/forms.py` | Форма создания задачи (поле title) |
| `todo/urls.py` | Маршруты с namespace "todo" |
| `todo/views.py` | Бизнес-логика (CBV) |
| `todo/templates/todo/base.html` | Базовый шаблон |
| `todo/templates/todo/list.html` | Список задач |
| `todo/templates/todo/create.html` | Форма создания |
| `todo/templates/todo/delete.html` | Подтверждение удаления |

---

## 3) Архитектура и взаимодействие компонентов

### Паттерн MTV (Model-Template-View)

```
Браузер (HTTP-запрос)
        ↓
config/urls.py  (корневой роутер)
        ↓
todo/urls.py    (роутер приложения, namespace "todo")
        ↓
todo/views.py   (классовые View)
        ↕
todo/models.py  (ORM → модель Tasks → SQLite)
        ↓
todo/templates/todo/*.html (рендеринг HTML)
        ↓
HTTP-ответ (HTML) → Браузер
```

### Взаимодействие компонентов

1. **Маршрутизация** — `config/urls.py` delegатирует запросы в `todo/urls.py` (`config/urls.py:2`).
2. **Представления (Views)** — `todo/views.py`:
   - `TasksListView` — все задачи;
   - `TasksActiveListView` — только активные (`is_active=True`);
   - `TasksCreateView` — создание через `TasksModelForm`;
   - `TasksUpdateIsDoneView` — переключение `is_active` и `completed_at`;
   - `TasksDeleteView` — GET (подтверждение) и POST (удаление).
3. **Модель (Model)** — `todo/models.py`, таблица `Tasks`. Чтения/записи через Django ORM.
4. **Шаблоны (Templates)** — расширяют `base.html`, формы через `crispy_forms_tags`, CSRF-токен во всех формах.
5. **Админка** — `todo/admin.py`, регистрация `Tasks` с полями `title`, `is_active`, `created_at`, `completed_at`.
6. **Статика** — CSS через `{% static %}`, JS через CDN.

---

## 4) Библиотеки и внешние зависимости с версиями

| Пакет | Версия | Назначение |
|-------|--------|------------|
| `Django` | `4.1.7` | Веб-фреймворк |
| `asgiref` | `3.6.0` | ASGI (требуется Django) |
| `sqlparse` | `0.4.3` | Парсинг SQL (требуется Django) |
| `pytz` | `2022.7.1` | Часовые пояса |
| `django-crispy-forms` | `2.0` | Рендеринг форм |
| `crispy-bootstrap3` | `2022.1` | Тема Bootstrap 3 для crispy |
| `crispy-bootstrap5` | `0.7` | Тема Bootstrap 5 (не используется) |
| `django-filter` | `22.1` | Фильтрация queryset |
| `djangorestframework` | `3.14.0` | REST API (не реализованы эндпоинты) |
| `black` | `23.1.0` | Форматтер кода (dev) |
| `isort` | `5.12.0` | Сортировка импортов (dev) |
| `mypy-extensions` | `1.0.0` | Расширения mypy (dev) |
| `click` | `8.1.3` | CLI (зависимость black) |
| `packaging` | `23.0` | Версии пакетов |
| `pathspec` | `0.11.0` | Совместимость с .gitignore |
| `platformdirs` | `3.0.0` | Папки платформы |
| `tomli` | `2.0.1` | Парсинг TOML |

**Зависимости по CDN** (`base.html`): jQuery 3.3.1 slim, Popper.js 1.14.6, Moment.js 2.23.0, Tempus Dominus Bootstrap 4, Font Awesome 4.7.0.

---

## 5) Модель данных (сущности, атрибуты, связи)

Единственная сущность — **`Tasks`** (`todo/models.py:4-12`).

### Сущность Tasks

| Атрибут | Тип | Параметры | Описание |
|---------|-----|-----------|----------|
| `id` | `BigAutoField` | `primary_key=True` | Идентификатор задачи |
| `title` | `CharField` | `max_length=255`, `verbose_name="Наименование"` | Название задачи |
| `is_active` | `BooleanField` | `default=True`, `verbose_name="Выполнена"` | Флаг выполнения |
| `created_at` | `DateTimeField` | `auto_now_add=True`, `verbose_name="Время создания"` | Время создания |
| `completed_at` | `DateTimeField` | `blank=True, null=True`, `verbose_name="Время завершения"` | Время завершения |

### Метаданные модели (`todo/models.py:14-16`)
- `verbose_name = "Задача"`
- `verbose_name_plural = "Задачи"`

### Связи
Связей нет (нет ForeignKey, OneToOne, ManyToMany). Нет привязки к пользователю (`auth.User`).

### История миграций (`todo/migrations/`)
1. `0001_add_item.py` — модель `Item` с полем `is_done` (default `False`);
2. `0002_rename_is_active.py` — переименование `is_done` → `is_active`;
3. `0003_rename_tasks.py` — модель `Tasks` (с `is_active`, default `True`) и удаление `Item`.

---

## 6) Обработка пользовательских запросов и работа с БД

### URL → View → Template/Модель

Маршруты (`todo/urls.py`, `app_name = "todo"`):

| URL | View | Метод | Действие |
|-----|------|-------|----------|
| `/` | `TasksListView` | GET | Все задачи (`list.html`) |
| `/active` | `TasksActiveListView` | GET | Активные задачи (`list.html`) |
| `/create` | `TasksCreateView` | GET/POST | Создание через `TasksModelForm` |
| `/update/<int:pk>` | `TasksUpdateIsDoneView` | POST | Переключение `is_active` / `completed_at` |
| `/delete/<int:pk>` | `TasksDeleteView` | GET/POST | Подтверждение и удаление |

Корневой роутер (`config/urls.py:2`): `admin/` → админка, остальное → `todo.urls`.

### Подробно по представлениям (`todo/views.py`)

**`TasksListView`** — `ListView`, модель `Tasks`, шаблон `todo/list.html`, все задачи без фильтрации.

**`TasksActiveListView`** — `View.get`, запрос `Tasks.objects.filter(is_active=True).all()`, ключ контекста `tasks_list`.

**`TasksCreateView`** — `CreateView`, `form_class = TasksModelForm` (только поле `title`), `success_url = reverse_lazy("todo:index")`.

**`TasksUpdateIsDoneView`** — `View.post(request, pk)`, переключает `is_active` и устанавливает/сбрасывает `completed_at`, ORM `update(...)`.

**`TasksDeleteView`** — `get` рендерит `delete.html`, `post` делает `delete()` и редирект.

### Работа с БД

- **Движок:** SQLite 3, файл `db.sqlite3` в корне (`config/settings.py:64-68`).
- **ORM:** все операции через Django ORM (`Tasks.objects.*`), нет raw SQL.
- **Миграции:** 3 файла в `todo/migrations/`, через `python manage.py migrate`.
- **Транзакции:** не управляются явно (авто-коммит Django).
- **Соединение:** ленивое, при первом запросе к БД.

### Особенности

1. Форма переключения статуса в `list.html` отправляется через `onclick="javascript:submit()"`.
2. `delete.html`: GET для подтверждения, POST для удаления.
3. `TasksListView` не фильтрует, `TasksActiveListView` фильтрует — дублирование логики.
4. `django-filter` и `djangorestframework` подключены, но не используются во views.
5. Нет аутентификации/авторизации, нет привязки к пользователю.
6. Поле `is_active` имеет семантику «не выполнено» (default `True`).

---

**Источники:** `/home/default/projects/todo-Cline/config/settings.py`, `config/urls.py`, `todo/models.py`, `todo/views.py`, `todo/urls.py`, `todo/forms.py`, `todo/admin.py`, `todo/migrations/*.py`, `todo/templates/todo/*.html`, `requirements.txt`, `PRACTICE.md`, `README.md`.
