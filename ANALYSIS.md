# ANALYSIS — анализ проекта ToDo (Python/Django)

> **Репозиторий:** `/home/default/projects/todo-Cline`
> **Статус:** актуально на 2026-11-01
> **Документ:** описывает текущее состояние кода, включая реализованные доработки.
> **Язык документации проекта:** русский

---

## 1. Назначение приложения и технологический стек

### 1.1 Назначение

Приложение — учебный **ToDo-менеджер** (список дел). Текущая версия позволяет:

- просматривать все задачи и отдельно только активные;
- создавать и редактировать задачи;
- задавать название, дедлайн, приоритет и категорию;
- переключать статус задачи «активна / выполнена»;
- удалять задачи с подтверждением;
- создавать категории;
- создавать подзадачи, отмечать их выполнение и удалять;
- видеть прогресс выполнения подзадач;
- сортировать список по приоритету, категории, названию, дате создания, дедлайну и прогрессу.

Проект используется в рамках практического занятия по AI Coding Agents (`PRACTICE.md`).

### 1.2 Технологический стек

| Компонент | Технология / версия | Источник |
|-----------|---------------------|----------|
| Язык | Python 3.14.4 | `.venv`, `python --version` |
| Веб-фреймворк | Django 6.1.2 | `requirements.txt`, `.venv` |
| База данных | SQLite 3 | `config/settings.py` |
| ORM | Django ORM | `todo/models.py` |
| Шаблонизатор | Django Templates | `config/settings.py`, `todo/templates/` |
| CSS | Bootstrap 5.1.3 (локальный `bootstrap.min.css`) | `todo/static/todo/css/bootstrap.min.css` |
| Формы | django-crispy-forms 2.7 + crispy-bootstrap3 2024.1 | `requirements.txt`, `todo/forms.py` |
| Календарь даты/времени | нативный HTML5 `input type="datetime-local"` | `todo/forms.py` |
| Локаль и время | `ru-RU`, `Europe/Moscow`, `USE_TZ=True` | `config/settings.py` |
| Статика | `STATIC_URL = "static/"`, файлы приложения | `config/settings.py`, `todo/static/` |

Дополнительно в шаблон `base.html` подключены по CDN: jQuery 3.3.1 slim, Popper.js 1.14.6, Moment.js 2.23.0, Tempus Dominus Bootstrap 4 и Font Awesome 4.7.0.

> **Важно:** `django-filter==26.2` установлен в виртуальном окружении, но не указан в `requirements.txt`, не добавлен в `INSTALLED_APPS` и нигде не используется. Это остаток прежней конфигурации.

---

## 2. Структура проекта

```text
todo-Cline/
├── ANALYSIS.md                  # этот документ
├── AUDIT.md                     # исторический технический аудит (частично устарел)
├── PRACTICE.md                  # описание практического задания
├── README.md                    # краткая инструкция запуска (частично устарела)
├── requirements.txt             # зафиксированные Python-зависимости
├── manage.py                    # CLI Django
├── db.sqlite3                   # локальная SQLite-база (в .gitignore)
├── config/
│   ├── settings.py              # настройки проекта
│   ├── urls.py                  # корневой URL-роутер
│   ├── asgi.py
│   └── wsgi.py
└── todo/
    ├── admin.py                 # регистрация моделей в админке
    ├── apps.py                  # TodoConfig
    ├── forms.py                 # формы задачи, подзадачи и категории
    ├── models.py                # Category, Tasks, Subtask
    ├── urls.py                  # маршруты приложения
    ├── views.py                 # классовые представления
    ├── migrations/              # миграции 0001–0005
    ├── static/todo/css/         # CSS
    └── templates/todo/          # HTML-шаблоны
```

### 2.1 Ключевые файлы

| Файл | Назначение |
|------|------------|
| `config/settings.py` | Настройки приложений, БД, шаблонов, middleware, локали |
| `config/urls.py` | `admin/` + подключение `todo.urls` |
| `todo/models.py` | Модели `Category`, `Tasks`, `Subtask` |
| `todo/views.py` | Список, сортировка, CRUD задач, категорий и подзадач |
| `todo/forms.py` | `TasksModelForm`, `SubtaskModelForm`, `CategoryModelForm` |
| `todo/urls.py` | Маршруты с namespace `todo` |
| `todo/admin.py` | Админка для трёх моделей |
| `todo/templates/todo/list.html` | Основной список задач, сортировка, подзадачи, прогресс |
| `todo/templates/todo/create.html`, `edit.html` | Создание и редактирование задачи |
| `todo/templates/todo/category_form.html` | Создание категории |
| `todo/templates/todo/subtask_form.html` | Создание подзадачи |
| `todo/templates/todo/delete.html` | Подтверждение удаления задачи |

---

## 3. Архитектура и взаимодействие компонентов

Приложение построено по паттерну **MTV (Model–Template–View)**.

```text
Браузер
  ↓ HTTP
config/urls.py
  ↓
todo/urls.py (namespace "todo")
  ↓
todo/views.py (ListView / CreateView / UpdateView / View)
  ↕
todo/models.py (Django ORM → SQLite)
  ↓
todo/templates/todo/*.html
  ↓
HTTP-ответ (HTML)
```

### 3.1 Компоненты

1. **Маршрутизация.** `config/urls.py` направляет `admin/` в админку, остальные запросы — в `todo.urls`.
2. **Представления.** `TasksListView` и `TasksActiveListView` отвечают за список и сортировку; `TasksCreateView` и `TasksUpdateView` — за формы задачи; отдельные `View` — за переключение статуса и удаление; `SubtaskCreateView`/`SubtaskDeleteView`/`SubtaskUpdateIsDoneView` — за подзадачи.
3. **Модели.** `Category`, `Tasks`, `Subtask`; связи `Category → Tasks` и `Tasks → Subtask`.
4. **Шаблоны.** Наследуются от `base.html`; формы рендерятся через `crispy_forms_tags`; во всех POST-формах есть `{% csrf_token %}`.
5. **Статика.** Локальный CSS Bootstrap 5.1.3; часть JS-библиотек подключена по CDN.

---

## 4. Зависимости

### 4.1 Python-зависимости из `requirements.txt`

| Пакет | Версия | Назначение |
|-------|--------|------------|
| `Django` | 6.1.2 | Веб-фреймворк |
| `asgiref` | 3.13.0 | ASGI-совместимость |
| `sqlparse` | 0.6.0 | Разбор SQL |
| `django-crispy-forms` | 2.7 | Рендеринг форм |
| `crispy-bootstrap3` | 2024.1 | Шаблоны crispy для Bootstrap 3 |

### 4.2 Фактически установлено в `.venv`

Дополнительно к списку выше установлен `django-filter==26.2`. Он не используется приложением и не включён в `INSTALLED_APPS`.

### 4.3 CDN-ресурсы

В `todo/templates/todo/base.html` подключены:

- jQuery 3.3.1 slim;
- Popper.js 1.14.6;
- Moment.js 2.23.0;
- Tempus Dominus Bootstrap 4 5.1.2;
- Font Awesome 4.7.0.

`Tempus Dominus` и `Moment.js` в текущей форме задачи не используются: дедлайн реализован нативным `datetime-local`. Скрипт инициализации `#datetimepicker1` в `base.html` остаётся мёртвым кодом.

---

## 5. Модель данных

### 5.1 Category

| Поле | Тип | Параметры |
|------|-----|-----------|
| `id` | `BigAutoField` | первичный ключ |
| `name` | `CharField` | `max_length=100`, `verbose_name="Название"` |

Поле `color` удалено из модели и из итоговой схемы БД миграцией `0005_remove_category_color.py`.

### 5.2 Tasks

| Поле | Тип | Параметры / значение по умолчанию |
|------|-----|-----------------------------------|
| `id` | `BigAutoField` | первичный ключ |
| `title` | `CharField` | `max_length=255`, обязательное |
| `is_active` | `BooleanField` | `default=True`; семантика — «задача активна / не выполнена» |
| `created_at` | `DateTimeField` | `auto_now_add=True` |
| `completed_at` | `DateTimeField` | `blank=True`, `null=True` |
| `priority` | `CharField` | `low` / `medium` / `high`, по умолчанию `medium` |
| `category` | `ForeignKey(Category)` | `blank=True`, `null=True`, `on_delete=SET_NULL` |
| `deadline` | `DateTimeField` | `blank=True`, `null=True` |

### 5.3 Subtask

| Поле | Тип | Параметры |
|------|-----|-----------|
| `id` | `BigAutoField` | первичный ключ |
| `task` | `ForeignKey(Tasks)` | `on_delete=CASCADE`, `related_name="subtasks"` |
| `title` | `CharField` | `max_length=255`, обязательное |
| `is_completed` | `BooleanField` | `default=False` |

### 5.4 Связи

```text
Category 1 ──── N Tasks
Tasks    1 ──── N Subtask
```

### 5.5 История миграций

1. `0001_add_item.py` — модель `Item` с полем `is_done` (`default=False`);
2. `0002_rename_is_active.py` — переименование `is_done` → `is_active`;
3. `0003_rename_tasks.py` — создание `Tasks` и удаление `Item`;
4. `0004_category_tasks_deadline_tasks_priority_and_more.py` — создание `Category` (тогда ещё с `color`), добавление `deadline`, `priority`, `category` в `Tasks`, создание `Subtask`;
5. `0005_remove_category_color.py` — удаление `Category.color`.

Итоговая схема не содержит `color`; упоминания остались только в исторических миграциях `0004`/`0005`.

---

## 6. Обработка пользовательских запросов

### 6.1 Маршруты

`todo/urls.py`, `app_name = "todo"`:

| URL | Имя | View | Методы |
|-----|-----|------|--------|
| `/` | `index` | `TasksListView` | GET |
| `/active` | `active` | `TasksActiveListView` | GET |
| `/create` | `create` | `TasksCreateView` | GET, POST |
| `/update/<int:pk>` | `update` | `TasksUpdateIsDoneView` | POST |
| `/edit/<int:pk>` | `edit` | `TasksUpdateView` | GET, POST |
| `/delete/<int:pk>` | `delete` | `TasksDeleteView` | GET, POST |
| `/category/create` | `category_create` | `TasksCategoryCreateView` | GET, POST |
| `/task/<int:task_pk>/subtask/create` | `subtask_create` | `SubtaskCreateView` | GET, POST |
| `/task/<int:task_pk>/subtask/<int:pk>/update` | `subtask_update` | `SubtaskUpdateIsDoneView` | POST |
| `/task/<int:task_pk>/subtask/<int:pk>/delete` | `subtask_delete` | `SubtaskDeleteView` | POST |

Корневой роутер `config/urls.py` подключает `admin/` и `todo.urls`.

### 6.2 Представления

#### `TasksListView`

- Модель: `Tasks`.
- Шаблон: `todo/list.html`.
- По умолчанию сортирует по `-created_at` (сначала новые).
- Поддерживает query-параметры `sort` и `dir`.
- Допустимые поля: `priority`, `category`, `title`, `created_at`, `deadline`, `progress`.
- Для заголовков таблицы формирует контекстные переменные `dir_priority`, `dir_category`, `dir_title`, `dir_created_at`, `dir_deadline`, `dir_progress`.

Логика сортировки (`get_queryset`):

| Поле | Сортировка |
|------|------------|
| `priority` | Аннотация `_priority_order`: `low=1`, `medium=2`, `high=3`; при `asc` — низкий → средний → высокий, при `desc` — наоборот |
| `category` | `F("category__name").asc/desc(nulls_last=True)` — задачи без категории всегда в конце |
| `deadline` | `F("deadline").asc/desc(nulls_last=True)` — задачи без дедлайна всегда в конце |
| `progress` | Аннотация `total=Count("subtasks")`, `completed=Count("subtasks", filter=Q(subtasks__is_completed=True))`, затем `progress_frac`; без подзадач доля равна `0.0` |
| `title` | `order_by("title")` / `order_by("-title")` |
| `created_at` | `order_by("created_at")` / `order_by("-created_at")` |

Направление:

- `dir=asc` → возрастание (`order = ""`);
- `dir=desc` → убывание (`order = "-"`);
- при повторном клике по тому же заголовку направление переключается;
- при переходе на другое поле по умолчанию используется `desc`.

#### `TasksActiveListView`

Наследуется от `TasksListView` и переопределяет только `get_queryset`:

```python
def get_queryset(self):
    return super().get_queryset().filter(is_active=True)
```

Благодаря этому активный список использует ту же сортировку, тот же шаблон и те же `dir_*`-переменные, без дублирования кода.

#### `TasksCreateView` и `TasksUpdateView`

- Используют `TasksModelForm`.
- Поля формы: `title`, `deadline`, `priority`, `category`.
- `success_url = reverse_lazy("todo:index")`.
- Дедлайн рендерится как `input type="datetime-local"`.

#### `TasksUpdateIsDoneView`

POST-переключение статуса задачи:

- если `is_active=True` → `is_active=False`, `completed_at=timezone.now()`;
- если `is_active=False` → `is_active=True`, `completed_at=None`;
- после изменения — редирект на `todo:index`.

#### `TasksDeleteView`

- GET — страница подтверждения `todo/delete.html`;
- POST — удаление задачи и редирект на `todo:index`;
- для несуществующего `pk` используется `get_object_or_404` → 404.

#### `TasksCategoryCreateView`

- Модель `Category`.
- Форма `CategoryModelForm`.
- Поле только `name`.
- После создания — редирект на `todo:index`.

#### `SubtaskCreateView`

- Модель `Subtask`, форма `SubtaskModelForm` (поле `title`).
- Родительская задача определяется по `task_pk` в URL и присваивается в `form_valid`.
- После создания — редирект на `todo:index`.

#### `SubtaskUpdateIsDoneView`

- POST по URL с `task_pk` и `pk`.
- Ищет подзадачу через `get_object_or_404(Subtask, id=pk, task_id=task_pk)`.
- Инвертирует `is_completed` и сохраняет.
- Редирект на `todo:index`.

#### `SubtaskDeleteView`

- POST по URL с `task_pk` и `pk`.
- Ищет подзадачу в рамках родительской задачи и удаляет.
- Редирект на `todo:index`.

### 6.3 Шаблоны

| Шаблон | Назначение |
|--------|------------|
| `base.html` | Каркас страницы, CSS, CDN-скрипты, навигация, футер |
| `list.html` | Таблица задач, сортировка, прогресс, подзадачи, управление |
| `create.html` | Создание задачи |
| `edit.html` | Редактирование задачи |
| `category_form.html` | Создание категории |
| `subtask_form.html` | Создание подзадачи |
| `delete.html` | Подтверждение удаления задачи |

#### `list.html`

Колонки таблицы:

1. `#` — `{{ forloop.counter }}`;
2. `Приоритет` — бейдж «Низкий» / «Средний» / «Высокий»;
3. `Категория` — название категории или `-`;
4. `Название` — `{{ model.title }}`;
5. `Время создания` — `{{ model.created_at|localtime }}` или `-`;
6. `Дедлайн` — `{{ model.deadline|localtime }}` или `-`;
7. `Прогресс` — `выполнено/всего (процент)`, например `1/2 (50%)`; без подзадач — `0/0 (0%)`;
8. `Управление` — переключатель статуса, «Редактировать», «Удалить», список подзадач, кнопка «+ Подзадача».

Для каждой подзадачи отображаются:

- чекбокс переключения выполнения (POST на `todo:subtask_update`, с CSRF);
- название;
- кнопка «Удалить» (POST на `todo:subtask_delete`, с CSRF).

Кнопка «+ Подзадача» отображается **у каждой задачи**, независимо от наличия подзадач.

Пустое состояние: если `tasks_list` пуст, выводится `<p>Список дел еще нет</p>`, а теги `<table>` и `</table>` не рендерятся — вся таблица находится внутри `{% if tasks_list %}`.

---

## 7. Реализованные функциональные требования

**FR-01. Просмотр всех задач.**
Главная страница `/` показывает все записи `Tasks` без фильтрации, по умолчанию — сначала новые.
Подтверждение: `TasksListView`, `todo/urls.py`, `list.html`.

**FR-02. Просмотр только активных задач.**
Страница `/active` показывает задачи с `is_active=True`.
Подтверждение: `TasksActiveListView`, маршрут `active`.

**FR-03. Создание задачи.**
Пользователь может указать название, дедлайн, приоритет и категорию.
Подтверждение: `TasksCreateView`, `TasksModelForm`, `create.html`.

**FR-04. Редактирование задачи.**
Страница `/edit/<pk>` позволяет изменить название, дедлайн, приоритет и категорию.
Подтверждение: `TasksUpdateView`, `edit.html`.

**FR-05. Переключение статуса задачи.**
POST на `/update/<pk>` меняет `is_active`; при завершении записывается `completed_at`, при возврате в активные — сбрасывается.
Подтверждение: `TasksUpdateIsDoneView`.

**FR-06. Удаление задачи с подтверждением.**
GET `/delete/<pk>` показывает подтверждение, POST удаляет задачу.
Подтверждение: `TasksDeleteView`, `delete.html`.

**FR-07. Создание категории.**
Пользователь может создать категорию, указав только название.
Подтверждение: `TasksCategoryCreateView`, `CategoryModelForm`, `category_form.html`.

**FR-08. Создание подзадачи.**
Подзадача создаётся для конкретной задачи через `/task/<task_pk>/subtask/create`.
Подтверждение: `SubtaskCreateView`, `SubtaskModelForm`, `subtask_form.html`.

**FR-09. Переключение выполнения подзадачи.**
POST на `subtask_update` инвертирует `is_completed`.
Подтверждение: `SubtaskUpdateIsDoneView`.

**FR-10. Удаление подзадачи.**
POST на `subtask_delete` удаляет подзадачу в рамках её задачи.
Подтверждение: `SubtaskDeleteView`, форма в `list.html`.

**FR-11. Кнопка «+ Подзадача» у каждой задачи.**
Кнопка не зависит от наличия подзадач и рендерится всегда.
Подтверждение: `list.html`.

**FR-12. Отображение прогресса.**
Для каждой задачи выводится `выполнено/всего` и процент; без подзадач — `0/0 (0%)`.
Подтверждение: `list.html`, фильтр `completed_count`, тег `widthratio`.

**FR-13. Сортировка по полям.**
Поддерживаются `priority`, `category`, `title`, `created_at`, `deadline`, `progress`.
Подтверждение: `ALLOWED_SORT_FIELDS`, `TasksListView.get_queryset`.

**FR-14. Переключение направления сортировки.**
Ссылки в заголовках содержат `dir_<поле>`; повторный клик переключает `asc`/`desc`; `desc` даёт убывание, `asc` — возрастание.
Подтверждение: `_next_dir`, `get_context_data`, `list.html`.

**FR-15. Семантический порядок приоритетов.**
При `asc`: низкий → средний → высокий; при `desc`: высокий → средний → низкий.
Подтверждение: аннотация `_priority_order` в `TasksListView`.

**FR-16. Задачи без категории и без дедлайна — в конце.**
При сортировке по категории и дедлайну используются `nulls_last=True` для обоих направлений.
Подтверждение: `F("category__name").asc/desc(nulls_last=True)`, `F("deadline").asc/desc(nulls_last=True)`.

**FR-17. Корректная разметка пустого списка.**
При отсутствии задач не рендерятся `<table>`, `<thead>` и `<tbody>`; выводится только сообщение.
Подтверждение: `list.html`.

**FR-18. CSRF-защита.**
Все POST-формы содержат `{% csrf_token %}`: создание/редактирование задачи, создание категории, создание подзадачи, переключение статуса, удаление подзадачи.
Подтверждение: шаблоны `create.html`, `edit.html`, `category_form.html`, `subtask_form.html`, `list.html`, `delete.html`.

**FR-19. Календарь для дедлайна.**
Поле дедлайна использует `DateTimeLocalInput` с `input_type="datetime-local"` и форматом `%Y-%m-%dT%H:%M`; браузер показывает календарь, значение при редактировании подставляется в локальном времени.
Подтверждение: `todo/forms.py`.

**FR-20. Цвет категории отсутствует.**
Поле `color` удалено из модели, формы, админки и итоговой схемы БД; остались только исторические миграции `0004`/`0005`.
Подтверждение: `todo/models.py`, `todo/forms.py`, `todo/admin.py`, `0005_remove_category_color.py`.

---

## 8. Бизнес-правила, проверки и ограничения

| Правило / ограничение | Текущая реализация | Подтверждение |
|-----------------------|--------------------|---------------|
| Название задачи обязательно | `title` — обязательное `CharField(max_length=255)` | `todo/models.py`, `TasksModelForm` |
| Новая задача активна | `is_active=True` по умолчанию | `todo/models.py` |
| Приоритет по умолчанию | `medium` | `todo/models.py` |
| Категория необязательна | `null=True`, `blank=True`, при удалении категории — `SET_NULL` | `todo/models.py` |
| Дедлайн необязателен | `null=True`, `blank=True` | `todo/models.py` |
| Время завершения | Устанавливается вручную при переводе задачи в выполненные; сбрасывается при возврате в активные | `TasksUpdateIsDoneView` |
| Подзадача принадлежит задаче | `ForeignKey(Tasks, on_delete=CASCADE, related_name="subtasks")` | `todo/models.py` |
| Название подзадачи обязательно | `CharField(max_length=255)` | `todo/models.py`, `SubtaskModelForm` |
| Прогресс без подзадач | `0/0 (0%)`, доля для сортировки — `0.0` | `list.html`, `TasksListView` |
| Сортировка только по допустимым полям | Белый список `ALLOWED_SORT_FIELDS` | `todo/views.py` |
| Неизвестное поле сортировки | Игнорируется, используется порядок по умолчанию `-created_at` | `TasksListView` |
| Некорректный `dir` | Приводится к `desc` | `_next_dir`, `get_queryset` |
| Задачи без категории/дедлайна | Всегда в конце при сортировке по соответствующему полю | `F(...).asc/desc(nulls_last=True)` |
| CSRF | Все POST-формы содержат `{% csrf_token %}` | шаблоны |
| Аутентификация | Отсутствует; все задачи общие | `todo/models.py`, `todo/views.py` |
| Уникальность названия | Не проверяется | `todo/models.py` |
| Валидация дедлайна | Нет запрета на прошедшую дату | `TasksModelForm` |
| Пагинация | Отсутствует | `TasksListView`, `list.html` |

---

## 9. Исправленные дефекты и изменения относительно исходной версии

### 9.1 Модель данных

- Добавлены модели `Category` и `Subtask`.
- В `Tasks` добавлены `priority`, `category`, `deadline`.
- В `Category` больше нет поля `color`: оно удалено из модели, формы, админки и итоговой схемы БД.
- История миграций: `0004` добавляет новые сущности и поля, `0005` удаляет `Category.color`.

### 9.2 Представления и сортировка

| Было / дефект | Стало |
|---------------|-------|
| `TasksActiveListView` дублировал логику списка и сортировки | Наследуется от `TasksListView`, переопределяет только `get_queryset` с фильтром `is_active=True` |
| В активном списке направление сортировки было инвертировано | Единая логика `asc`/`desc` для обоих списков |
| Сортировка приоритета в активном списке была алфавитной | Аннотация `_priority_order`: `low=1`, `medium=2`, `high=3` |
| `order_by("category__isnull", ...)` вызывал `FieldError` | `F("category__name").asc/desc(nulls_last=True)` |
| `order_by("deadline__isnull", ...)` вызывал `FieldError` | `F("deadline").asc/desc(nulls_last=True)` |
| Прогресс в активном списке считался по числу выполненных, а не по доле | Единая аннотация `total` / `completed` / `progress_frac` |
| `Tasks.objects.get()` / `.filter().first()` могли дать 500 при неверном `pk` | `get_object_or_404` в update/delete-представлениях |

### 9.3 Шаблон `list.html`

- Кнопка «+ Подзадача» вынесена из условия `{% if subtasks %}` и отображается у каждой задачи.
- Добавлена кнопка удаления подзадачи: POST на `todo:subtask_delete` с CSRF.
- В колонке «Прогресс» выводится `выполнено/всего (процент)`, например `1/2 (50%)`; без подзадач — `0/0 (0%)`.
- `<table>`, `<thead>`, `<tbody>` и `</table>` полностью находятся внутри `{% if tasks_list %}`; пустой список не содержит тегов таблицы.
- Ссылки сортировки используют актуальные `dir_<поле>`; повторный клик переключает направление.
- Задачи без категории и без дедлайна отображаются/сортируются в конце при соответствующей сортировке.

### 9.4 Формы

- Дедлайн больше не текстовое поле: используется `DateTimeLocalInput` с `type="datetime-local"`, формат `%Y-%m-%dT%H:%M`.
- При редактировании значение дедлайна подставляется в локальном времени.
- Поле цвета категории полностью удалено; `CategoryModelForm` содержит только `name`.

### 9.5 Конфигурация и зависимости

- Проект работает на Django 6.1.2 (в исходной версии был Django 4.1.7).
- `requirements.txt` содержит актуальный набор: Django 6.1.2, crispy-forms 2.7, crispy-bootstrap3 2024.1, asgiref, sqlparse.
- В текущих `INSTALLED_APPS` и `requirements.txt` нет `django-filter` и `djangorestframework`; при этом `django-filter` всё ещё установлен в `.venv` как остаток прежней конфигурации.
- В `settings.py` заданы `ALLOWED_HOSTS = ["127.0.0.1", "localhost"]`, `DEFAULT_AUTO_FIELD = BigAutoField`, `LANGUAGE_CODE = "ru-RU"`, `TIME_ZONE = "Europe/Moscow"`.
- CSS Bootstrap в проекте — 5.1.3, при этом формы рендерятся через `crispy-bootstrap3`; это известное несоответствие оформления.

---

## 10. Остаточные ограничения и риски

1. **Настройки не для production.** `SECRET_KEY` — временный dev-ключ, `DEBUG=True`, `ALLOWED_HOSTS` ограничен `127.0.0.1` и `localhost`. Перед развёртыванием нужны реальный секрет, выключенный debug, HTTPS-настройки и корректные хосты.
2. **Нет аутентификации и авторизации.** Любой посетитель может создавать, редактировать и удалять любые задачи, категории и подзадачи. Привязки к пользователю нет.
3. **Нет пагинации.** Список выводится целиком; при большом количестве задач возможны проблемы с производительностью.
4. **Нет автоматизированных тестов в репозитории.** Проверки выполнялись вручную/через Django test client и не сохранены как тестовый набор.
5. **Документация частично устарела.** `README.md` до сих пор предлагает устанавливать `django_filter`; `AUDIT.md` описывает исходную версию (Django 4.1.7, пустой `SECRET_KEY`, отсутствие категорий и подзадач) и не отражает текущее состояние.
6. **Неиспользуемая зависимость.** `django-filter==26.2` установлен в `.venv`, но отсутствует в `requirements.txt`, `INSTALLED_APPS` и коде.
7. **Несоответствие CSS и crispy.** Локальный CSS — Bootstrap 5.1.3, а формы рендерятся пакетом `crispy-bootstrap3`; возможны визуальные расхождения.
8. **Мёртвый код в `base.html`.** Moment.js, Tempus Dominus и скрипт `$("#datetimepicker1").datetimepicker(...)` больше не используются: дедлайн работает через нативный `datetime-local`. CDN-ресурсы можно удалить.
9. **Хрупкое переключение чекбоксов.** В `list.html` используется `onclick="javascript:submit()"`; вызов не привязан явно к конкретной форме, а в строке несколько форм. Поведение зависит от браузера и может быть ненадёжным. Надёжнее указывать конкретную форму или использовать отдельные обработчики.
10. **Категории неполные.** Реализовано только создание категории; нет отдельного списка, редактирования и удаления категорий.
11. **Подзадачи неполные.** Нет редактирования названия подзадачи; доступны создание, переключение выполнения и удаление.
12. **Нет проверок уникальности и дат.** Названия задач/категорий/подзадач не уникальны; прошедшие дедлайны не запрещены; при равных значениях сортировки нет стабильного tie-breaker.
13. **Семантика `is_active`.** `True` означает «активная / не выполненная», что противоречит названию поля и может путать; шаблон инвертирует значение для чекбокса.
14. **Мелкие дефекты шаблонов.** В `create.html`/`edit.html` указан `enctype="multipart/form-data"` при отсутствии файловых полей; в `delete.html` текст «удалить задача» вместо «удалить задачу».
15. **SQLite.** База подходит для локальной разработки, но не для многопользовательской production-нагрузки.
16. **Исторические упоминания цвета.** `Category.color` удалён из рабочего кода и схемы, но остаётся в миграциях `0004` (добавление) и `0005` (удаление) — это нормальная история миграций.

---

## 11. Проверка текущего состояния

Выполненные команды:

```bash
.venv/bin/python manage.py check
# System check identified no issues (0 silenced).

.venv/bin/python manage.py makemigrations --check --dry-run
# No changes detected
```

Дополнительно через Django test client проверялось:

- создание подзадачи через форму с CSRF и её удаление POST-запросом;
- отображение прогресса `1/2 (50%)`, `2/2 (100%)`, `0/0 (0%)`;
- сортировка по `priority`, `category`, `deadline`, `progress`, `title` в направлениях `asc` и `desc`;
- переключение `dir_*` при повторном клике;
- задачи без категории и без дедлайна в конце списка;
- активный список (наследование сортировки и фильтрация `is_active=True`);
- пустой список без тегов `<table>`;
- страница создания задачи с `input type="datetime-local"` и сохранение даты без сдвига;
- отсутствие поля цвета в модели, форме, админке и таблице БД.

Тестовые данные создавались в транзакции и откатывались; локальная база не заполнялась тестовыми записями.

