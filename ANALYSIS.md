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

> Раздел подготовлен по заданию №2 практики (см. `PRACTICE.md`). Описана только фактически реализованная функциональность; выявленные дефекты вынесены в отдельный подраздел и в состав требований не включены.

## 1. Основные функциональные возможности приложения

- **Просмотр списка задач** — главная страница показывает таблицу всех задач: порядковый номер, статус выполнения (чекбокс), название, время создания, время завершения и кнопку удаления — `todo/views.py` (`TasksListView`, строки 10–14), `todo/templates/todo/list.html` (строки 13–73).
- **Создание задачи** — веб-форма с единственным полем «Наименование» — `todo/views.py` (`TasksCreateView`, строки 27–32), `todo/forms.py` (`TasksModelForm`, строки 6–11), `todo/templates/todo/create.html`.
- **Отметка выполнения и снятие отметки** — переключатель-чекбокс в списке меняет статус задачи и фиксирует/очищает время завершения — `todo/views.py` (`TasksUpdateIsDoneView.post`, строки 35–45), `todo/templates/todo/list.html` (строки 32–41).
- **Удаление задачи с подтверждением** — двухшаговое удаление (страница подтверждения → удаление) — `todo/views.py` (`TasksDeleteView`, строки 48–60), `todo/templates/todo/delete.html`.
- **Просмотр только невыполненных («активных») задач** — отдельный URL `/active` — `todo/views.py` (`TasksActiveListView.get`, строки 17–24), `todo/urls.py` (строка 15).
- **Администрирование** — стандартная админка Django для сущности «Задача» с поиском по названию — `todo/admin.py` (строки 6–10), `config/urls.py` (строка 4).

## 2. Основные сценарии взаимодействия пользователя с приложением

### Сценарий А. Просмотр списка задач (GET `/`)

1. Пользователь открывает главную страницу.
2. Маршрут `""` → `TasksListView` (`todo/urls.py`, строка 14).
3. View выполняет выборку всех задач (стандартный queryset `Tasks.objects.all()` для `ListView`) и рендерит `todo/list.html` (`todo/views.py`, строки 10–14).
4. Если задач нет — выводится сообщение «Список дел еще нет» (`list.html`, строки 68–70); иначе — таблица с колонками «#», «Выполено», «Название», «Время создания», «Время выполнения», «Управление» (`list.html`, строки 13–66). Даты выводятся с фильтром `|localtime`.
5. На странице доступны действия: «Добавить» (ссылка на `todo:create`), чекбокс статуса и «Удалить» для каждой задачи.

### Сценарий Б. Создание задачи (GET `/create` → POST `/create`)

1. Пользователь нажимает «Добавить» на главной странице (`list.html`, строка 10).
2. `TasksCreateView` отображает форму `TasksModelForm` с единственным полем «Наименование» (`todo/views.py`, строки 27–32; `todo/forms.py`, строки 9–11; рендеринг через crispy-forms — `create.html`, строки 13–19).
3. Пользователь вводит название и нажимает «Сохранить».
4. Система валидирует форму: поле обязательно и не длиннее 255 символов (правило поля `title` модели `Tasks` — `todo/models.py`, строка 7).
5. При корректных данных создаётся запись: `title` — введённое значение; `is_active=True` (значение по умолчанию — `todo/models.py`, строка 8); `created_at` — текущее время (`auto_now_add` — строка 9); `completed_at` — пусто.
6. Система перенаправляет на главную страницу (`success_url = reverse_lazy("todo:index")` — `todo/views.py`, строка 32).
7. При некорректных данных форма отображается повторно с сообщениями об ошибках (стандартное поведение `CreateView`/crispy-forms).

### Сценарий В. Отметка выполнения / снятие отметки (POST `/update/<id>`)

1. Пользователь кликает по чекбоксу в строке задачи; скрипт `onclick="javascript:submit()"` отправляет форму POST на `todo:update` (`list.html`, строки 32–41).
2. `TasksUpdateIsDoneView.post` находит задачу по id (`todo/views.py`, строка 40).
3. Если задача «активна» (`is_active=True`): статус меняется на «выполнена» — `is_active=False`, `completed_at=timezone.now()` (`views.py`, строки 41–42).
4. Если задача выполнена (`is_active=False`): отметка снимается — `is_active=True`, `completed_at=None` (`views.py`, строки 43–44).
5. Система перенаправляет на главную страницу; чекбокс отражает новое состояние (отмечен, когда задача выполнена: `{% if not model.is_active %}` — `list.html`, строка 35), в колонке «Время выполнения» появляется или исчезает время.

### Сценарий Г. Удаление задачи (GET `/delete/<id>` → POST `/delete/<id>`)

1. Пользователь нажимает «Удалить» в строке задачи (`list.html`, строки 60–62).
2. GET-запрос показывает страницу подтверждения с названием задачи («Вы уверены, что хотите удалить задача: ...?») — `TasksDeleteView.get` (`todo/views.py`, строки 51–55), шаблон `todo/templates/todo/delete.html`.
3. Пользователь нажимает «Удалить»; POST-запрос удаляет запись (`Tasks.objects.filter(id=pk).delete()` — `views.py`, строка 59).
4. Система перенаправляет на главную страницу (`views.py`, строка 60).

### Сценарий Д. Просмотр активных (невыполненных) задач (GET `/active`)

1. Пользователь открывает адрес `/active` напрямую (ссылок из интерфейса на него нет).
2. `TasksActiveListView.get` фильтрует `is_active=True` и рендерит тот же шаблон `todo/list.html` (`views.py`, строки 20–24).
3. Пользователь видит таблицу только с невыполненными задачами; чекбокс и удаление работают так же, как на главной.

### Сценарий Е. Администрирование (GET `/admin/`)

1. Администратор открывает `/admin/` и входит под учётной записью с правами персонала (стандартный механизм Django).
2. `TasksAdmin` показывает список задач с колонками `title`, `is_active`, `created_at`, `completed_at`, поиск по `title` и форму редактирования полей `title`, `is_active`, `completed_at` (`todo/admin.py`, строки 6–10).

## 3. Бизнес-правила, проверки и ограничения

- **Название задачи обязательно и ограничено 255 символами**: `title = models.CharField(max_length=255)` без `blank=True` (`todo/models.py`, строка 7); в форме только это поле (`todo/forms.py`, строка 11). Проверка выполняется на уровне формы Django и БД.
- **Новая задача всегда создаётся невыполненной**: `is_active` имеет `default=True` и отсутствует в форме (`todo/models.py`, строка 8; `todo/forms.py`, строка 11).
- **Семантика статуса**: `is_active=True` означает «активна / не выполнена», `is_active=False` — «выполнена» (`todo/views.py`, строки 41–44). Название поля и его `verbose_name="Выполнена"` этой логике противоречат (см. раздел 5).
- **Время создания фиксируется автоматически** при вставке записи (`auto_now_add=True`, `todo/models.py`, строка 9) и нигде не редактируется (поля нет ни в пользовательской форме, ни в админке — `todo/forms.py`, `todo/admin.py`).
- **Время завершения управляется только переключателем статуса**: заполняется текущим временем сервера при выполнении и обнуляется при снятии отметки (`todo/views.py`, строки 42, 44). В форме создания поле недоступно (`todo/forms.py`, строка 11); в админке редактируется вручную (`todo/admin.py`, строка 10).
- **Удаление — двухшаговое с подтверждением**: отдельный GET-экран перед POST-удалением (`todo/views.py`, строки 51–60).
- **Все POST-запросы защищены CSRF-токеном**: `{% csrf_token %}` в `list.html` (строка 33), `create.html` (строка 14), `delete.html` (строка 10).
- **После любого изменения выполняется redirect на список** (PRG-паттерн): создание — `views.py`, строка 32; переключение статуса — строка 45; удаление — строка 60.
- **Права доступа**: пользовательская часть не требует аутентификации — любой посетитель может просматривать, создавать, менять статус и удалять задачи (проверок пользователя в `todo/views.py` нет); доступ к админке ограничен стандартным механизмом Django (`config/urls.py`, строка 4).
- **Пустой список** отображается сообщением, а не пустой таблицей (`todo/templates/todo/list.html`, строки 68–70).
- **Сортировка и пагинация отсутствуют**: в queryset нет `order_by`, в `ListView` нет `paginate_by` (`todo/views.py`, строки 10–14) — порядок задач определяется БД (SQLite).
- **Редактирование названия после создания не предусмотрено**: для `Tasks` есть только форма создания (`todo/forms.py`), переключение статуса и удаление; формы правки `title` на пользовательских страницах нет.
- **Проверка существования задачи при смене статуса отсутствует**: view обращается к `item.is_active` без проверки на `None` (`todo/views.py`, строки 40–41).
- **Время хранится и отображается с учётом часовых поясов**: `USE_TZ=True`, `TIME_ZONE="Europe/Moscow"` (`config/settings.py`, строки 89–93); в шаблоне — фильтр `|localtime` (`list.html`, строки 47, 54).

## 4. Функциональные требования

1. **Система должна отображать список всех задач на главной странице.** Маршрут `""` направлен на `TasksListView` (`todo/urls.py`, строка 14); класс-представление `TasksListView` рендерит `todo/list.html` с queryset модели `Tasks` (`todo/views.py`, строки 10–14).
2. **Система должна выводить для каждой задачи: порядковый номер, чекбокс статуса, название, время создания, время завершения и кнопку удаления.** Таблица с этими колонками — `todo/templates/todo/list.html`, строки 13–66.
3. **Система должна выводить сообщение «Список дел еще нет», когда задач нет.** Условие `{% if tasks_list %}` с веткой `{% else %}` — `todo/templates/todo/list.html`, строки 13, 68–70.
4. **Пользователь должен иметь возможность перейти к форме создания задачи со списка.** Ссылка «Добавить» на `todo:create` — `todo/templates/todo/list.html`, строка 10.
5. **Система должна предоставлять форму создания задачи с полем «Наименование».** `TasksCreateView` использует `TasksModelForm` (`todo/views.py`, строки 27–32); форма включает единственное поле `title` (`todo/forms.py`, строки 6–11); рендеринг формы — `todo/templates/todo/create.html`, строки 13–19.
6. **Система должна отклонять создание задачи без названия или с названием длиннее 255 символов.** Поле `title = models.CharField(max_length=255)` без `blank=True` (`todo/models.py`, строка 7) проверяется формой `TasksModelForm` (`todo/forms.py`).
7. **Система должна создавать новую задачу в статусе «не выполнена».** `is_active = models.BooleanField(default=True)` и отсутствие поля в форме (`todo/models.py`, строка 8; `todo/forms.py`, строка 11).
8. **Система должна автоматически фиксировать время создания задачи.** `created_at = models.DateTimeField(auto_now_add=True)` — `todo/models.py`, строка 9.
9. **После успешного создания задачи система должна перенаправлять пользователя на главную страницу.** `success_url = reverse_lazy("todo:index")` — `todo/views.py`, строка 32.
10. **Пользователь должен иметь возможность отметить задачу выполненной и снять отметку через чекбокс в списке.** Форма с `action="{% url 'todo:update' model.id %}"` и чекбоксом, отправляемая кликом — `todo/templates/todo/list.html`, строки 32–41; обработчик `TasksUpdateIsDoneView.post` — `todo/views.py`, строки 35–45; маршрут — `todo/urls.py`, строка 17.
11. **При отметке выполнения система должна установить статус «выполнена» и зафиксировать текущее время завершения.** `Tasks.objects.filter(id=pk).update(is_active=False, completed_at=timezone.now())` — `todo/views.py`, строка 42.
12. **При снятии отметки система должна вернуть статус «не выполнена» и очистить время завершения.** `Tasks.objects.filter(id=pk).update(is_active=True, completed_at=None)` — `todo/views.py`, строка 44.
13. **Чекбокс должен отображать состояние задачи: отмечен для выполненной, не отмечен для невыполненной.** `{% if not model.is_active %}` → `checked` — `todo/templates/todo/list.html`, строки 35–39.
14. **После изменения статуса система должна перенаправлять пользователя на главную страницу.** `return redirect("todo:index")` — `todo/views.py`, строка 45.
15. **Пользователь должен иметь возможность запросить подтверждение удаления задачи.** GET `/delete/<pk>` рендерит `delete.html` с названием задачи — `TasksDeleteView.get` (`todo/views.py`, строки 51–55), шаблон `todo/templates/todo/delete.html`, маршрут `todo/urls.py`, строка 18.
16. **Система должна удалять задачу по POST-запросу и перенаправлять на главную страницу.** `Tasks.objects.filter(id=pk).delete()` и `redirect("todo:index")` — `TasksDeleteView.post`, `todo/views.py`, строки 57–60.
17. **Система должна предоставлять отдельную страницу со списком только невыполненных (активных) задач.** Маршрут `"active"` → `TasksActiveListView` (`todo/urls.py`, строка 15); `TasksActiveListView.get` фильтрует `is_active=True` и рендерит `todo/list.html` (`todo/views.py`, строки 17–24).
18. **Система должна отображать время в часовом поясе Europe/Moscow.** `TIME_ZONE="Europe/Moscow"`, `USE_TZ=True` (`config/settings.py`, строки 89–93); применение фильтра `|localtime` в шаблоне (`todo/templates/todo/list.html`, строки 47, 54).
19. **Система должна защищать все POST-формы от CSRF-атак.** Токены `{% csrf_token %}` — `todo/templates/todo/list.html` (строка 33), `todo/templates/todo/create.html` (строка 14), `todo/templates/todo/delete.html` (строка 10); промежуточное ПО `CsrfViewMiddleware` — `config/settings.py`, строка 38.
20. **Все страницы приложения должны использовать общий каркас оформления.** Наследование `{% extends "todo/base.html" %}` во всех страничных шаблонах (`list.html`, строка 1; `create.html`, строка 1; `delete.html`, строка 1); подключение Bootstrap 5.1.3 и собственного CSS в `base.html` (строки 10–11); навигация «Главная» в шапке и подвале (`base.html`, строки 32, 49).
21. **Администратор должен иметь возможность управлять задачами через админку: просматривать список с колонками (название, статус, время создания, время завершения), искать по названию и редактировать поля.** `TasksAdmin` с `list_display`, `search_fields`, `fields` — `todo/admin.py`, строки 6–10; подключение админки — `config/urls.py`, строка 4.

## 5. Неоднозначности, противоречия и возможные дефекты реализации

*(в требования не включены)*

1. **Инвертированная семантика статуса.** `is_active` с `default=True` и `verbose_name="Выполнена"` (`todo/models.py`, строка 8) фактически означает «не выполнена»: чекбокс отмечен при `not model.is_active` (`list.html`, строка 35), а `TasksUpdateIsDoneView` трактует `True` как «активна» (`views.py`, строки 41–44). По имени поля «активна» логично, по подписи «Выполнена» — нет.
2. **Ошибка 500 при смене статуса несуществующей задачи.** `TasksUpdateIsDoneView.post` берёт `Tasks.objects.filter(id=pk).first()` и сразу обращается к `item.is_active` без проверки на `None` (`todo/views.py`, строки 40–41) — при несуществующем id возникает `AttributeError`.
3. **Ошибка 500 при запросе подтверждения удаления несуществующей задачи.** `TasksDeleteView.get` использует `Tasks.objects.get(id=pk)` без обработки `DoesNotExist` (`todo/views.py`, строка 54).
4. **«Тихое» удаление несуществующей задачи.** `TasksDeleteView.post` удаляет через `filter(...).delete()` без проверки, что запись существовала (`todo/views.py`, строка 59) — запрос к несуществующему id выглядит как успех.
5. **Неатомарное переключение статуса.** Чтение и обновление — два отдельных запроса без транзакции (`views.py`, строки 40–44); при конкурентных запросах возможны гонки.
6. **Страница `/active` не связана из интерфейса.** Ни один шаблон не содержит ссылки на `todo:active` (`base.html`, `list.html`, `create.html`, `delete.html`); страница достижима только прямым вводом адреса, её назначение неоднозначно (дублирует главную с фильтром).
7. **Маршруты без завершающего слеша.** `path("active")`, `path("create")`, `path("update/<int:pk>")`, `path("delete/<int:pk>")` (`todo/urls.py`, строки 15–18) — те же адреса со слешем дают 404.
8. **Мёртвая конфигурация REST.** `REST_FRAMEWORK` с пагинацией и фильтрами задан (`config/settings.py`, строки 28–32), но `rest_framework` не включён в `INSTALLED_APPS` (строки 11–23) и ни один API-маршрут не объявлен (`config/urls.py`, `todo/urls.py`); `django_filters` подключён, но нигде не используется.
9. **Несоответствие пакетов оформления форм и CSS-фреймворка.** crispy-forms настроен на `bootstrap3` (`config/settings.py`, строки 25–26), а разметка использует Bootstrap 5.1.3 (`base.html`, строка 10; `bootstrap.min.css`, строка 2); `crispy_bootstrap5` закомментирован (`settings.py`, строки 20–21).
10. **Неиспользуемые фронтенд-зависимости.** jQuery (кроме `submit()`), Popper, Moment.js, Tempus Dominus подключаются в `base.html` (строки 12–23); инициализация datetimepicker ссылается на несуществующий элемент `#datetimepicker1` (`base.html`, строки 55–61).
11. **Нет пагинации и сортировки** при потенциально большом списке: `ListView` без `paginate_by` и `ordering` (`todo/views.py`, строки 10–14); настроенная DRF-пагинация (`PAGE_SIZE=2`) не применяется.
12. **Пустое или пробельное название допустимо.** `CharField` без `blank=True` отклоняет только пустую строку; строка из пробелов проходит валидацию (`todo/models.py`, строка 7).
13. **Опечатки в пользовательском интерфейсе**: «Выполено» (`list.html`, строка 18), «Список дел еще нет» (`list.html`, строка 69), «удалить задача» (`delete.html`, строка 12).
14. **Потеря данных в истории миграций.** `0003_rename_tasks.py` создаёт `Tasks` и удаляет `Item` (`DeleteModel`) без переноса данных (строки 11–52); между миграциями менялась и семантика: `is_done` с `default=False` (`0001`, строка 28) → `is_active` с `default=True` (`0003`, строка 30).
15. **Изменение названия задачи после создания невозможно** через пользовательский интерфейс (есть только создание, переключение статуса и удаление) — возможная неполнота функциональности, если предполагалось редактирование.
16. **Нет подтверждения при смене статуса** — чекбокс отправляет форму сразу по клику (`list.html`, строки 36–38); случайный клик сразу меняет данные.