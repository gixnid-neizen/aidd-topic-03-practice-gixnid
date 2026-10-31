# ANALYSiS — Анализ проекта ToDo (Python/Django)

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

---

## 7) Восстановленные функциональные требования

### 7.1 Основные функциональные возможности приложения

На основании кода реализованы следующие возможности:

1. **Просмотр списка всех задач** — отображение всех записей модели `Tasks` без фильтрации.
2. **Просмотр только активных задач** — фильтрация по `is_active=True`.
3. **Создание новой задачи** — ввод только названия (`title`) через форму.
4. **Переключение статуса задачи** — смена флага `is_active` между активной и выполненной, с установкой/сбросом `completed_at`.
5. **Удаление задачи** — двухэтапная процедура: страница подтверждения (GET) и фактическое удаление (POST).

---

### 7.2 Основные сценарии взаимодействия пользователя

**Сценарий 1. Просмотр всех задач**
1. Пользователь открывает главную страницу (`/`).
2. Система использует `TasksListView` (`todo/views.py:10-14`), маршрут `""` (`todo/urls.py:14`).
3. Отображается шаблон `todo/templates/todo/list.html` со всеми задачами из `Tasks.objects.all()`.

**Сценарий 2. Просмотр только активных задач**
1. Пользователь переходит по URL `/active`.
2. Система использует `TasksActiveListView` (`todo/views.py:17-24`), маршрут `"active"` (`todo/urls.py:15`).
3. Выполняется запрос `Tasks.objects.filter(is_active=True).all()`.
4. Отображается шаблон `todo/templates/todo/list.html` только с активными задачами.

**Сценарий 3. Создание новой задачи**
1. Пользователь нажимает кнопку «Добавить» на странице списка (`list.html:10`), ссылка `{% url 'todo:create' %}`.
2. Открывается шаблон `todo/templates/todo/create.html` с формой `TasksModelForm` (`todo/forms.py:6-10`, только поле `title`).
3. Пользователь вводит название и нажимает «Сохранить» — выполняется POST.
4. Срабатывает `TasksCreateView` (`todo/views.py:27-32`), маршрут `"create"` (`todo/urls.py:16`).
5. После успешного создания система перенаправляет на главную страницу (`success_url = reverse_lazy("todo:index")`).

**Сценарий 4. Переключение статуса задачи (выполнена / не выполнена)**
1. Пользователь кликает на переключатель (switch) в строке задачи в таблице (`list.html:32-41`).
2. Форма отправляет POST на `{% url 'todo:update' model.id %}`.
3. Срабатывает `TasksUpdateIsDoneView.post(request, pk)` (`todo/views.py:35-45`), маршрут `"update/<int:pk>"` (`todo/urls.py:17`).
4. Если `is_active` была `True` — устанавливается `False` и `completed_at = timezone.now()`; если была `False` — устанавливается `True` и `completed_at = None`.
5. Система перенаправляет на главную страницу (`redirect("todo:index")`).

**Сценарий 5. Удаление задачи**
1. Пользователь нажимает «Удалить» в строке задачи (`list.html:60-63`), ссылка `{% url 'todo:delete' model.id %}`.
2. Выполняется GET на `/delete/<int:pk>`, срабатывает `TasksDeleteView.get` (`todo/views.py:52-55`), маршрут `"delete/<int:pk>"` (`todo/urls.py:18`).
3. Отображается шаблон `todo/templates/todo/delete.html` с названием задачи (`{{ item.title }}`).
4. Пользователь нажимает кнопку «Удалить» — выполняется POST.
5. Срабатывает `TasksDeleteView.post` (`todo/views.py:58-59`), выполняется `Tasks.objects.filter(id=pk).delete()`.
6. Система перенаправляет на главную страницу.

---

### 7.3 Бизнес-правила, проверки и ограничения

| Правило / ограничение | Описание | Подтверждение в коде |
|-----------------------|----------|----------------------|
| Название задачи обязательно | Поле `title` обязательно в `ModelForm`, `max_length=255` | `todo/forms.py:6-10`, `todo/models.py:7` |
| Новая задача создаётся активной | `is_active` по умолчанию `True` | `todo/models.py:8` |
| При выполнении задачи записывается время завершения | `completed_at = timezone.now()` при смене на `is_active=False` | `todo/views.py:42` |
| При возврате к активному времени завершения сбрасывается | `completed_at = None` при смене на `is_active=True` | `todo/views.py:44` |
| Все задачи общие, не привязаны к пользователю | Нет связи с `auth.User`, нет аутентификации в представлениях | `todo/models.py`, `todo/views.py` |
| CSRF-защита на всех формах | `{% csrf_token %}` во всех шаблонах форм | `list.html:33`, `create.html:14`, `delete.html:10` |
| Удаление требует подтверждения | GET показывает страницу подтверждения, POST выполняет удаление | `todo/views.py:52-59`, `todo/templates/todo/delete.html` |
| Переключение статуса только через POST | `TasksUpdateIsDoneView` имеет только метод `post` | `todo/views.py:39` |

---

### 7.4 Функциональные требования (нумерованный список)

Каждое требование содержит ссылку на файл и функцию/класс, которые его подтверждают.

**FR-01.** Система должна отображать на главной странице (`/`) полный список всех задач без фильтрации.  
Подтверждение: `todo/views.py` — класс `TasksListView` (строки 10–14); `todo/urls.py` — маршрут `""`, имя `index` (строка 14); `todo/templates/todo/list.html`.

**FR-02.** Система должна отображать только активные задачи (`is_active=True`) по адресу `/active`.  
Подтверждение: `todo/views.py` — класс `TasksActiveListView`, метод `get` (строки 17–24); `todo/urls.py` — маршрут `"active"`, имя `active` (строка 15).

**FR-03.** Система должна позволять создавать новую задачу, заполняя только поле названия (`title`).  
Подтверждение: `todo/forms.py` — класс `TasksModelForm`, `fields = ["title"]` (строки 6–10); `todo/views.py` — класс `TasksCreateView` (строки 27–32); `todo/templates/todo/create.html`.

**FR-04.** После успешного создания задачи система должна перенаправлять пользователя на главную страницу.  
Подтверждение: `todo/views.py` — `success_url = reverse_lazy("todo:index")` в `TasksCreateView` (строка 32).

**FR-05.** Система должна позволять переключать статус задачи между активной и выполненной. При переходе в выполненное состояние устанавливается `completed_at` (текущее время), при возврате к активному — `completed_at` сбрасывается в `None`.  
Подтверждение: `todo/views.py` — метод `TasksUpdateIsDoneView.post` (строки 39–45); `todo/urls.py` — маршрут `"update/<int:pk>"`, имя `update` (строка 17).

**FR-06.** Система должна позволять удалять задачу после подтверждения пользователем. GET-запрос отображает страницу подтверждения с названием задачи; POST-запрос выполняет фактическое удаление.  
Подтверждение: `todo/views.py` — класс `TasksDeleteView`, методы `get` (строки 52–55) и `post` (строки 58–59); `todo/templates/todo/delete.html`; `todo/urls.py` — маршрут `"delete/<int:pk>"`, имя `delete` (строка 18).

**FR-07.** Все формы создания, переключения статуса и удаления должны быть защищены CSRF-токеном.  
Подтверждение: `todo/templates/todo/list.html` (строка 33), `todo/templates/todo/create.html` (строка 14), `todo/templates/todo/delete.html` (строка 10) содержат `{% csrf_token %}`.

**FR-08.** Задачи не привязаны к конкретным пользователям; все задачи доступны любому посетителю без аутентификации и авторизации.  
Подтверждение: отсутствие `LoginRequiredMixin`, `PermissionRequiredMixin` или любой связи с `auth.User` в `todo/models.py` и `todo/views.py`; отсутствие зависимостей от аутентификации в представлениях.

---

### 7.5 Неоднозначности, противоречия и возможные дефекты реализации

1. **Инвертированная семантика поля `is_active`.** Поле называется `is_active` и имеет `default=True`, но по сути означает «не выполнено» (активно = не выполнено). В миграции `0002_rename_is_active.py` оно переименовано из `is_done`, но семантика осталась противоречивой названию (`todo/models.py:8`, `todo/migrations/0002_rename_is_active.py`).

2. **Дублирование логики отображения списка.** `TasksListView` выводит все задачи без фильтрации, тогда как `TasksActiveListView` выводит только активные. Оба используют один шаблон `list.html`, но разную логику формирования queryset (`todo/views.py:10-24`).

3. **Риск нео intentional переключения статуса.** В `list.html` форма переключения статуса отправляется через `onclick="javascript:submit()"` на чекбоксе (`list.html:36,38`). Одиночный клик по чекбоксу сразу инициирует запрос на изменение статуса без дополнительного подтверждения.

4. **Отсутствие валидации уникальности названия.** Можно создать несколько задач с одинаковым `title`; ограничения уникальности в модели нет (`todo/models.py:7`, `todo/forms.py:6-10`).

5. **Отсутствие пагинации.** Список задач выводится полностью без постраничной навигации, несмотря на наличие `django-filter` и настройки пагинации в `REST_FRAMEWORK` (`config/settings.py:28-32`), которые не применяются к HTML-представлениям.

6. **Неиспользуемые зависимости.** `django-filter` и `djangorestframework` подключены в `INSTALLED_APPS` и `REST_FRAMEWORK` (`config/settings.py:22,28-32`), но API-эндпоинты и фильтрация queryset не реализованы во Views.

7. **Отсутствие обработки «задача не найдена» (404).** В `TasksDeleteView.get` используется `Tasks.objects.get(id=pk)` (`todo/views.py:54`), что при несуществующем `pk` вызовет `DoesNotExist` и приведёт к ошибке 500 вместо страницы 404.

8. **Потенциальная ошибка `AttributeError` в `TasksUpdateIsDoneView`.** Используется `Tasks.objects.filter(id=pk).first()` (`todo/views.py:40`); если задача не найдена, `item` будет `None`, и обращение к `item.is_active` вызовет `AttributeError`.

9. **Отсутствие разграничения прав доступа.** Любой пользователь может создать, переключить статус и удалить любую задачу, так как нет привязки к пользователю и нет проверок прав (`todo/views.py`, `todo/models.py`).

10. **Нет использования `TasksActiveListView` из шаблона.** Навигация в `base.html` ведёт только на `todo:index` (`base.html:32,49`); ссылка на `/active` не используется в интерфейсе, хотя маршрут существует.
