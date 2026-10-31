
---

## 8) Технический аудит проекта

### 8.1 Устаревшие библиотеки и зависимости

| Пакет | Версия в проекте | Актуальная версия | Статус | Файл |
|-------|-----------------|-------------------|--------|------|
| Django | `4.1.7` | `6.1.2` (LTS: `5.2.x`) | **Критически устарел** | `requirements.txt:6` |
| djangorestframework | `3.14.0` | `3.18.3` | Устарел | `requirements.txt:9` |
| django-crispy-forms | `2.0` | `2.7` | Устарел | `requirements.txt:7` |
| django-filter | `22.1` | `26.1` | **Критически устарел** | `requirements.txt:8` |
| crispy-bootstrap3 | `2022.1` | неизвестно | Возможно устарел | `requirements.txt:4` |
| crispy-bootstrap5 | `0.7` | неизвестно | Возможно устарел | `requirements.txt:5` |
| asgiref | `3.6.0` | более новая | Устарел | `requirements.txt:1` |
| sqlparse | `0.4.3` | более новая | Устарел | `requirements.txt:16` |
| pytz | `2022.7.1` | более новая | Устарел | `requirements.txt:15` |
| black | `23.1.0` | более новая | Устарел (dev) | `requirements.txt:2` |
| isort | `5.12.0` | более новая | Устарел (dev) | `requirements.txt:10` |

**Риски:**
- Django 4.1.7 больше не получает исправления безопасности (поддержка завершена). В проекте известны уязвимости, исправленные в версиях 4.2.x, 5.x и 6.x.
- django-filter 22.1 не совместим с новыми версиями Django без изменений.
- Отсутствует `pyproject.toml` / `setup.cfg` для управления зависимостями.

---

### 8.2 Проблемы совместимости с современным Python и Django

| Проблема | Описание | Файл |
|----------|----------|------|
| Django 4.1.7 не поддерживает Python 3.12+ | Django 4.1 поддерживает только Python 3.8–3.11. На Python 3.12+ проект не запустится. | `requirements.txt:6`, `manage.py` |
| `crispy_bootstrap5` установлен, но не используется | Пакет `crispy-bootstrap5==0.7` в `requirements.txt`, но в `INSTALLED_APPS` закомментирован (`# "crispy_bootstrap5"`). | `config/settings.py:20`, `requirements.txt:5` |
| `django-filter` и `djangorestframework` подключены, но не используются | Оба добавлены в `INSTALLED_APPS` и `REST_FRAMEWORK`, но во Views нет API-эндпоинтов и фильтрации queryset. | `config/settings.py:22,28-32` |
| Отсутствует `DEFAULT_AUTO_FIELD` в `INSTALLED_APPS`-контексте приложений | Хотя в `settings.py` и `apps.py` указан `BigAutoField`, это может вызвать конфликты при миграции на новые Django. | `config/settings.py:97`, `todo/apps.py:5` |

---

### 8.3 Проблемы конфигурации (settings.py)

| Проблема | Описание | Файл |
|----------|----------|------|
| **`SECRET_KEY = ""`** | Пустой секретный ключ. Критическая уязвимость безопасности — CSRF, сессии, сброс паролей и защита подделываются. | `config/settings.py:4` |
| **`DEBUG = True`** | Включен режим отладки. При развёртывании на продакшене раскрывает чувствительную информацию (traceback, переменные окружения, структуру кода). | `config/settings.py:6` |
| **`ALLOWED_HOSTS = []`** | Пустой список разрешённых хостов. В продакшене Django будет отвергать все запросы с `DisallowedHost`. | `config/settings.py:8` |
| Отсутствие `STATIC_ROOT` и `STATICFILES_DIRS` | Статика собирается только через `APP_DIRS`, нет указания куда собирать `collectstatic`. | `config/settings.py:95` |
| Отсутствие `MEDIA_URL` и `MEDIA_ROOT` | Нет поддержки загрузки файлов (хотя в `create.html` указан `enctype="multipart/form-data"`, но модель не имеет `FileField`). | `config/settings.py`, `todo/templates/todo/create.html:13` |
| Отсутствие настроек безопасности HTTPS | Нет `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS`. | `config/settings.py` |
| `CRISPY_TEMPLATE_PACK = "bootstrap3"` | Используется Bootstrap 3, который сам по себе устарел (не поддерживается с 2018). | `config/settings.py:26` |

---

### 8.4 Проблемы миграций и модели данных

| Проблема | Описание | Файл |
|----------|----------|------|
| Странная история миграций | `0001_add_item` создаёт модель `Item`, `0002` переименовывает поле, `0003` создаёт `Tasks` и удаляет `Item`. Нет прямой миграции к текущему состоянию `Tasks`. | `todo/migrations/0001_add_item.py`, `0002_rename_is_active.py`, `0003_rename_tasks.py` |
| Поле `is_active` имеет инвертированную семантику | `default=True` означает «не выполнено», но название поля suggère обратное. Путаница при чтении кода и поддержке. | `todo/models.py:8` |
| Отсутствует привязка к пользователю | Нет ForeignKey к `auth.User` или кастомной модели пользователя. Все задачи общие, нет изоляции данных между пользователями. | `todo/models.py` |
| Нет индексов на часто запрашиваемых полях | `is_active`, `created_at` используются в фильтрации и сортировке, но без индексов. | `todo/models.py:7-9` |
| `completed_at` не имеет `auto_now` | Заполняется вручную в представлении, что может привести к неконсистентности. | `todo/models.py:10-12` |

---

### 8.5 Проблемы в представлениях (views.py)

| Проблема | Описание | Файл |
|----------|----------|------|
| **`AttributeError` при несуществующем `pk`** | `TasksUpdateIsDoneView.post`: `item = Tasks.objects.filter(id=pk).first()` может вернуть `None`, затем `item.is_active` вызовет `AttributeError`. | `todo/views.py:40-41` |
| **`DoesNotExist` → ошибка 500** | `TasksDeleteView.get`: `Tasks.objects.get(id=pk)` без `try/except` или `get_object_or_404`. При неверном `pk` пользователь получит 500 вместо 404. | `todo/views.py:54` |
| Дублирование логики списка | `TasksListView` (все задачи) и `TasksActiveListView` (только активные) дублируют шаблон `list.html`, но с разной логикой queryset. | `todo/views.py:10-24` |
| Нет пагинации | Вывод всех задач без постраничной навигации. При большом объёме данных — проблемы с производительностью. | `todo/views.py:10-14`, `todo/templates/todo/list.html` |
| Нет проверки прав доступа | Любой пользователь может создать, изменить статус и удалить любую задачу. | `todo/views.py` (все классы) |
| `TasksListView` не использует `get_queryset` | Фильтрация жёстко задана через `model = Tasks`, нет гибкости для расширения. | `todo/views.py:10-13` |

---

### 8.6 Проблемы в шаблонах и статике

| Проблема | Описание | Файл |
|----------|----------|------|
| Bootstrap 3 устарел | Bootstrap 3 больше не поддерживается (EOL 2018). Отсутствуют современные компоненты и исправления безопасности. | `config/settings.py:26`, `todo/static/todo/css/bootstrap.min.css` |
| `enctype="multipart/form-data"` без `FileField` | Форма создания задачи отправляет multipart, но модель не имеет полей для файлов. | `todo/templates/todo/create.html:13` |
| JS-библиотеки через CDN без локальных fallback | jQuery, Popper.js, Moment.js, Tempus Dominus подключены по CDN. При недоступности CDN интерфейс ломается. | `todo/templates/todo/base.html:12-23` |
| Ссылка на `/active` не используется в UI | Маршрут существует, но в `base.html` навигация ведёт только на `todo:index`. | `todo/templates/todo/base.html:32,49` |

---

### 8.7 Критические проблемы безопасности (высокий приоритет)

1. **Пустой `SECRET_KEY`** — `config/settings.py:4`. Требует немедленного исправления перед любым развёртыванием.
2. **`DEBUG = True`** — `config/settings.py:6`. Необходимо выключить для продакшена.
3. **`ALLOWED_HOSTS = []`** — `config/settings.py:8`. Приведёт к ошибкам в продакшене.
4. **Отсутствие аутентификации и авторизации** — любые действия с задачами доступны анонимным пользователям.
5. **Отсутствие защиты от CSRF в некоторых путях** — хотя в формах есть `{% csrf_token %}`, отсутствие проверок прав делает приложение уязвимым к несанкционированным действиям.

---

### 8.8 Рекомендации по приоритетам

| Приоритет | Проблема | Необходимое действие |
|-----------|----------|---------------------|
| **Критический** | `SECRET_KEY = ""`, `DEBUG = True`, `ALLOWED_HOSTS = []` | Заполнить secrets, выключить Debug, настроить хосты |
| **Высокий** | Django 4.1.7 → 5.2.x LTS или 6.x | Обновить Django и все зависимые пакеты |
| **Высокий** | Отсутствие обработки 404 и `AttributeError` | Добавить `get_object_or_404`, проверку на `None` |
| **Средний** | Отсутствие пагинации, привязки к пользователю | Добавить пагинацию и ForeignKey к User |
| **Средний** | Устаревшие зависимости (crispy-forms, drf, django-filter) | Обновить до актуальных версий |
| **Низкий** | Bootstrap 3, неиспользуемые пакеты | Перейти на Bootstrap 5, удалить неиспользуемые приложения |

**Источники:** все файлы проекта по путям `/home/default/projects/todo-Cline/config/settings.py`, `config/urls.py`, `todo/models.py`, `todo/views.py`, `todo/urls.py`, `todo/forms.py`, `todo/admin.py`, `todo/migrations/*.py`, `todo/templates/todo/*.html`, `requirements.txt`.
