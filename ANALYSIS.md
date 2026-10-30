# ANALYSIS.md — Проект ToDo (Python/Django)

> Репозиторий проекта: <https://github.com/aidd-mcs/aidd-topic-03-practice>
> Документ подготовлен по материалам практического занятия №3 «AI Coding Agents на практике» (см. `PRACTICE.md`).

---

# Анализ исходного кода

## 1. Назначение и технологический стек

**Назначение** — простое веб-приложение «Список дел» (ToDo): просмотр списка задач, отметка выполнения, создание и удаление задач. Это учебный проект «Практическое занятие №3. AI Coding Agents на практике» (заявлено в `PRACTICE.md`, строки 1–4). Приложение создавалось начинающими разработчиками и может содержать дефекты (`PRACTICE.md`, строки 12–16).

**Стек:**

| Слой | Технология | Источник |
|---|---|---|
| Язык | Python (в `.venv` — 3.14.4) | `.venv/pyvenv.cfg` (строка 3) |
| Фреймворк | Django 4.1.7 (MTV, class-based views) | `requirements.txt` (строка 6), `config/settings.py` (строки 11–23) |
| БД | SQLite через ORM Django | `config/settings.py` (строки 64–69) |
| Формы | django-crispy-forms 2.0 с template pack bootstrap3 | `requirements.txt` (строка 7), `config/settings.py` (строки 25–26) |
| Фильтрация | django-filter 22.1 (сконфигурирован, в views не используется) | `config/settings.py` (строки 28–32) |
| REST API | Django REST Framework 3.14.0 (настроен, но не подключён — см. замечания) | `config/settings.py` (строки 28–32) |
| Frontend | Bootstrap 5.1.3 (локально), jQuery 3.3.1, Popper 1.14.6, Font Awesome 4.7.0, Moment.js 2.23.0, Tempus Dominus 5.1.2 (CDN) | `todo/templates/todo/base.html` (строки 10–23), `todo/static/todo/css/bootstrap.min.css` (строка 2) |
| Шаблонизация | Django Templates (серверный рендеринг) | `config/settings.py` (строки 46–60) |

Это классическое **серверное (server-rendered) MPA**, без SPA-фреймворка и без реально работающего REST API.

## 2. Структура проекта

```
todo-deepseek/
├── config/                  # Пакет конфигурации Django-проекта
│   ├── __init__.py          # пустой, маркер пакета
│   ├── settings.py          # настройки: приложения, middleware, БД, шаблоны, i18n
│   ├── urls.py              # корневая таблица маршрутов (admin/ + todo.urls)
│   ├── wsgi.py              # entry point для WSGI-серверов
│   └── asgi.py              # entry point для ASGI-серверов
├── todo/                    # Django-приложение «todo»
│   ├── __init__.py          # пустой
│   ├── apps.py              # класс TodoConfig (name="todo")
│   ├── models.py            # модель Tasks
│   ├── views.py             # 5 class-based views
│   ├── urls.py              # маршруты приложения (namespace "todo")
│   ├── forms.py             # TasksModelForm
│   ├── admin.py             # регистрация Tasks в админке
│   ├── migrations/          # 3 миграции (0001–0003)
│   ├── templates/todo/      # шаблоны: base/list/create/delete.html
│   └── static/todo/css/     # bootstrap.min.css, sticky-footer-navbar.css
├── manage.py                # CLI-утилита Django (DJANGO_SETTINGS_MODULE=config.settings)
├── requirements.txt         # закреплённые версии Python-зависимостей
├── README.md                # краткая инструкция установки/запуска
├── PRACTICE.md              # задание практической работы (не код приложения)
├── .gitignore               # исключения: .venv, db.sqlite3, .env и т.д.
└── .venv/                   # виртуальное окружение (сейчас содержит только pip 25.1.1)
```

Назначение ключевых файлов:

- **`manage.py`** (строки 7–18) — стандартная точка входа: задаёт `DJANGO_SETTINGS_MODULE="config.settings"` и вызывает `django.core.management.execute_from_command_line`.
- **`config/settings.py`** — центр конфигурации: `INSTALLED_APPS` (стандартные приложения Django + `todo.apps.TodoConfig` + `crispy_forms` + `crispy_bootstrap3` + `django_filters`), `MIDDLEWARE` (7 стандартных), БД SQLite, шаблоны, `LANGUAGE_CODE="ru-RU"`, `TIME_ZONE="Europe/Moscow"`.
- **`config/urls.py`** (строка 4) — корневой маршрутизатор: `/admin/` и все остальные URL делегируются в `todo.urls`.
- **`config/wsgi.py` / `config/asgi.py`** (строки 7) — объекты `application` для развёртывания (приложение синхронное, работает и как WSGI, и как ASGI).
- **`todo/urls.py`** — маршруты приложения с namespace `todo` и именами `index`, `active`, `create`, `update`, `delete`.
- **`todo/views.py`** — вся бизнес-логика.
- **`todo/models.py`** — модель данных.
- **`todo/migrations/`** — история изменения схемы БД.
- **`todo/templates/todo/`** — 4 шаблона: общий каркас `base.html` и страницы `list/create/delete`.
- **`.gitignore`** (строки 10–11) — БД `db.sqlite3` и `.venv/` не попадают в репозиторий.

## 3. Архитектура и взаимодействие компонентов

Классическая **MTV-архитектура Django (Model–Template–View)** — см. `todo/views.py`, `todo/models.py`, `todo/templates/`:

```
Браузер (HTML/Bootstrap/jQuery)
        │ HTTP
        ▼
WSGI/ASGI entry point (config/wsgi.py, config/asgi.py)
        ▼
MIDDLEWARE (Security, Session, Common, CSRF, Auth, Messages, XFrameOptions)  ← settings.py:34-42
        ▼
URL Router: config/urls.py → include("todo.urls")  (namespace "todo")
        ▼
View (todo/views.py) ──┐
        │              │
        │              ▼
        │        Model/ORM (todo/models.py → SQLite db.sqlite3)
        ▼
Template (todo/templates/todo/*.html, crispy-forms)
        ▼
HTTP-ответ (HTML)
```

Ключевые особенности взаимодействия:

- **Все views — class-based**: `ListView` (список), `CreateView` (создание через `ModelForm`), и три самописных `View` с методами `get`/`post` (фильтр активных, переключение статуса, удаление) — `todo/views.py` (строки 10–60).
- **View обращаются к БД напрямую через ORM** (`Tasks.objects...`); отдельного service-слоя или репозитория нет — вся логика в views.
- **Форма создания** — `TasksModelForm` на базе `forms.ModelForm`, отображается через `crispy_forms` (`as_crispy_field`) в `todo/templates/todo/create.html` (строки 8–17).
- **Переключение «Выполнена»** реализовано не формой Django, а вручную: чекбокс с `onclick="javascript:submit()"` отправляет POST на `todo:update` — `todo/templates/todo/list.html` (строки 32–41).
- **Шаблоны наследуют общий каркас** `base.html` через `{% extends %}`; навигация построена на теге `{% url 'todo:index' %}` — `todo/templates/todo/base.html` (строка 32).
- **CSRF-защита** на всех POST-формах (`{% csrf_token %}` — `list.html` (строка 33), `create.html` (строка 14), `delete.html` (строка 10)).
- **Аутентификации нет**: в шаблонах и views не используется пользователь; стандартные auth-middleware/приложения подключены, но вход не требуется.
- **DRF/django-filter настроены, но фактически не работают**: конфиг `REST_FRAMEWORK` задан в `settings.py` (строки 28–32), однако `rest_framework` отсутствует в `INSTALLED_APPS` и в `urls.py` нет ни одного API-маршрута.
- **Frontend-библиотеки** (jQuery, Popper, Moment.js, Tempus Dominus) подключены, но реально используется только jQuery; инициализация datetimepicker в `base.html` (строки 55–61) ссылается на несуществующий элемент `#datetimepicker1`.

## 4. Библиотеки и внешние зависимости

### Python (закреплено в `requirements.txt`)

| Пакет | Версия | Роль в проекте |
|---|---|---|
| Django | 4.1.7 | веб-фреймворк (фактически весь бэкенд) |
| django-crispy-forms | 2.0 | рендеринг форм (create.html) |
| crispy-bootstrap3 | 2022.1 | template pack для crispy-forms (активен) |
| crispy-bootstrap5 | 0.7 | template pack (установлен, но закомментирован в settings) |
| django-filter | 22.1 | фильтры (сконфигурирован в REST_FRAMEWORK, не используется в коде) |
| djangorestframework | 3.14.0 | REST (настроен, не подключён в INSTALLED_APPS) |
| asgiref | 3.6.0 | транзитивная зависимость Django |
| sqlparse | 0.4.3 | транзитивная зависимость Django |
| pytz | 2022.7.1 | часовые пояса |
| black | 23.1.0 | форматировщик (инструмент разработки) |
| isort | 5.12.0 | сортировка импортов (инструмент разработки) |
| click | 8.1.3 | транзитивная (black/isort) |
| mypy-extensions | 1.0.0 | транзитивная |
| packaging | 23.0 | транзитивная |
| pathspec | 0.11.0 | транзитивная (black) |
| platformdirs | 3.0.0 | транзитивная (black) |
| tomli | 2.0.1 | транзитивная (black) |

### Frontend/статика

- **Bootstrap v5.1.3** — локальный файл `todo/static/todo/css/bootstrap.min.css` (строка 2), подключается в `todo/templates/todo/base.html` (строка 10).
- CDN-скрипты в `base.html` (строки 12–23): jQuery 3.3.1 slim, Popper.js 1.14.6, Font Awesome 4.7.0, Moment.js 2.23.0, Tempus Dominus Bootstrap 4 5.1.2.
- Собственный CSS: `todo/static/todo/css/sticky-footer-navbar.css` — один отступ для `main > .container`.

> **Примечание о версиях и окружении.** Зависимости — эпохи 2022–2023 гг. и закреплены жёстко (`==`). В текущем `.venv` (Python 3.14.4, см. `.venv/pyvenv.cfg`) установлен **только pip 25.1.1** — Django и прочие пакеты не установлены, т.е. приложение в этом окружении сейчас не запускается. Есть и несоответствие: template pack `bootstrap3` для crispy-forms, при том что в разметке используется Bootstrap 5.1.3.

## 5. Модель данных

**Единственная сущность — `Tasks` (Задача)**, определена в `todo/models.py` (строки 4–16):

| Атрибут | Тип поля | Ограничения/поведение | verbose_name |
|---|---|---|---|
| `id` | `BigAutoField` | первичный ключ (неявно, `DEFAULT_AUTO_FIELD` в `config/settings.py`, строка 97) | — |
| `title` | `CharField(max_length=255)` | обязательный | «Наименование» |
| `is_active` | `BooleanField(default=True)` | флаг «не выполнена» (семантика инвертирована относительно названия) | «Выполнена» |
| `created_at` | `DateTimeField(auto_now_add=True)` | заполняется автоматически при создании | «Время создания» |
| `completed_at` | `DateTimeField(blank=True, null=True)` | ставится вручную при отметке выполнения | «Время завершения» |

- **Связей с другими таблицами нет** — модель полностью автономна; в проекте не используются внешние ключи и связанные сущности (пользователи, категории и т.п.).
- Таблица в БД получит имя `todo_tasks` (по умолчанию Django), `Meta.verbose_name = "Задача"`, `verbose_name_plural = "Задачи"` — `todo/models.py` (строки 14–16).
- **История миграций** (папка `todo/migrations/`):
  1. `0001_add_item.py` — создаёт модель `Item` с полем `is_done` (`BooleanField(default=False)`).
  2. `0002_rename_is_active.py` — переименовывает `is_done` → `is_active`.
  3. `0003_rename_tasks.py` — создаёт новую модель `Tasks` (с `is_active` `default=True`) и **удаляет** модель `Item`.

  > Дефект схемы: `DeleteModel("Item")` в 0003 уничтожает и данные; а поле `is_active` в `models.py` имеет `default=True`, тогда как переключатель в `todo/views.py` (строки 41–44) трактует `True` как «не выполнена», а `False` — как «выполнена», что противоречит названию поля.

## 6. Обработка пользовательских запросов и работа с БД

### Таблица маршрутов

Корневой роутер `config/urls.py` (строка 4) делегирует все запросы (кроме `/admin/`) в `todo/urls.py` (строки 13–19):

| URL | View | Метод | Поведение |
|---|---|---|---|
| `/` | `TasksListView` (`ListView`) | GET | все задачи, шаблон `todo/list.html`, контекст `tasks_list` |
| `/active` | `TasksActiveListView` | GET | только задачи с `is_active=True`, тот же шаблон |
| `/create` | `TasksCreateView` (`CreateView`) | GET/POST | форма `TasksModelForm` (поле `title`), при успехе redirect на `todo:index` |
| `/update/<int:pk>` | `TasksUpdateIsDoneView` | POST | переключение статуса выполнения |
| `/delete/<int:pk>` | `TasksDeleteView` | GET/POST | подтверждение удаления / удаление |

### Поток обработки запроса

1. **Маршрутизация**: `config/urls.py` → `todo/urls.py` сопоставляет URL с CBV.
2. **View** (`todo/views.py`):
   - *Список*: `ListView` по модели `Tasks` сам формирует queryset `Tasks.objects.all()` и рендерит `todo/templates/todo/list.html`; «активный» список вручную фильтрует `Tasks.objects.filter(is_active=True).all()` (строка 23).
   - *Создание*: `CreateView` с `form_class = TasksModelForm` (`todo/forms.py`, строки 6–11, редактируется только `title`) сохраняет запись через `ModelForm.save()` и делает redirect на `todo:index` (строки 27–32).
   - *Переключение статуса*: `POST` находит запись `Tasks.objects.filter(id=pk).first()`; если `is_active` — обновляет `is_active=False` и `completed_at=timezone.now()`, иначе `is_active=True`, `completed_at=None`; затем redirect (строки 35–45).
   - *Удаление*: `GET` рендерит подтверждение `todo/templates/todo/delete.html` с объектом `Tasks.objects.get(id=pk)`; `POST` выполняет `Tasks.objects.filter(id=pk).delete()` и redirect (строки 48–60).
3. **Шаблоны**: наследуют `todo/templates/todo/base.html` (подключает Bootstrap и прочие ассеты); список отображает таблицу с чекбоксом-переключателем и кнопкой «Удалить» (`list.html`, строки 27–66); время выводится с фильтром `|localtime` (`list.html`, строки 47, 54); форма создания использует crispy-тег `as_crispy_field` (`create.html`, строки 15–17).

### Работа с БД

- **СУБД**: SQLite, файл `db.sqlite3` в корне проекта — `config/settings.py` (строки 64–69). Файл БД исключён из git (`.gitignore`, строки 10–11) и в текущем рабочем дереве отсутствует.
- **Доступ**: только через ORM Django (`Tasks.objects...`); сырого SQL в коде нет. Используются: `.all()`, `.filter(...)`, `.first()`, `.get(...)`, `.update(...)`, `.delete()` — `todo/views.py` (строки 23, 40–44, 54, 59).
- **Схема**: создаётся/обновляется миграциями `python manage.py migrate` (`README.md`, строка 11); старт сервера — `python manage.py runserver` (`README.md`, строка 14).

### Замечания (обнаруженные при чтении дефекты и несоответствия)

- `SECRET_KEY` пуст, `DEBUG=True`, `ALLOWED_HOSTS=[]` — `config/settings.py` (строки 4–8).
- `rest_framework` настроен в `REST_FRAMEWORK`, но не добавлен в `INSTALLED_APPS`; API-маршрутов нет — конфиг мёртвый (`config/settings.py`, строки 28–32 против строк 11–23).
- `crispy_bootstrap5` закомментирован, активен `bootstrap3`, но фронтенд использует Bootstrap 5 (`config/settings.py`, строки 20–21).
- В `todo/views.py` (строки 40–41) `item` берётся через `.first()`, затем обращение `item.is_active` без проверки на `None` → `AttributeError` при несуществующем id; в delete-GET используется `.get()` → `DoesNotExist` (в шаблоне никак не обрабатывается).
- Удаление в `TasksDeleteView` выполнено через GET-подтверждение, а не `DeleteView`.
- Маршруты без завершающего слеша (`/create`, `/active`, `/update/<pk>`) — при включённом `APPEND_SLASH` такие URL могут давать 404.
- `base.html` загружает jQuery/Popper/Moment/Tempus Dominus, которые фактически не используются (кроме jQuery), и инициализирует datetimepicker для отсутствующего элемента (`base.html`, строки 55–61).
- Семантика `is_active` инвертирована: `default=True` означает «не выполнена», а verbose_name поля — «Выполнена» (`todo/models.py`, строка 8); в списке чекбокс отмечен, только когда задача **выполнена** (`not model.is_active` — `list.html`, строка 35).
- Опечатки в шаблонах: «Выполено» (`list.html`, строка 18), «Список дел еще нет» (`list.html`, строка 69), «удалить задача» (`delete.html`, строка 12).
- Зависимости 2022–2023 гг., не совместимы с Python 3.14 в текущем `.venv` (там установлен только pip 25.1.1) — см. `.venv/pyvenv.cfg` и `requirements.txt`.

---

# Восстановленные требования

<!-- TODO: раздел будет заполнен после выполнения задания №2 практики (см. PRACTICE.md) -->

(Здесь будет описание восстановленных функциональных требований: основные функциональные возможности, сценарии взаимодействия пользователя с приложением, бизнес-правила, проверки и ограничения, а также выявленные неоднозначности и дефекты.)