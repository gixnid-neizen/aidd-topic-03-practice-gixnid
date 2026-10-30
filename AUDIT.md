# AUDIT.md — Технический аудит проекта ToDo (Python/Django)

> Дата аудита: 31.10.2026.
> Метод: только чтение кода и конфигурации; изменения в проект не вносились (создан лишь этот файл).
> Актуальные версии пакетов получены из PyPI (`https://pypi.org/pypi/<name>/json`) на дату аудита.
> Совместимость версий Django/Python — по официальной документации Django (`docs.djangoproject.com/en/stable/faq/install/`) и классификаторам PyPI.

---

## 1. Резюме

1. **Приложение в текущем окружении не запускается.** В `.venv` установлен только pip (`.venv/pyvenv.cfg`); зависимостей нет, а стек из `requirements.txt` несовместим с Python 3.14.4.
2. **Весь стек зависимостей устарел на 3–4 года.** Django 4.1.7 вне поддержки (EOL) с декабря 2023 и не получает security-обновлений.
3. **Критические проблемы конфигурации:** пустой `SECRET_KEY`, `DEBUG=True`, `ALLOWED_HOSTS=[]`, мёртвая конфигурация REST (`REST_FRAMEWORK` без DRF в `INSTALLED_APPS`), потеря данных в истории миграций.
4. **Несоответствия фронтенда:** template pack `bootstrap3` для crispy-forms при Bootstrap 5.1.3 в разметке; Popper 1.14.6 при Bootstrap 5 (нужен Popper 2); неиспользуемые CDN-библиотеки.

---

## 2. Устаревшие библиотеки и зависимости

Источник версий проекта — `requirements.txt` (все строки). Актуальные версии — PyPI на 31.10.2026.

### 2.1. Python-зависимости (`requirements.txt`)

| Пакет | Версия в проекте | Актуальная версия | Комментарий |
|---|---|---|---|
| Django | 4.1.7 | **6.1.2** | EOL с декабря 2023 (конец extended support); без security-фиксов. LTS-альтернатива: 5.2. |
| django-crispy-forms | 2.0 | **2.7** | 2.7 поддерживает Django 5.2–6.1 и Python 3.10–3.14; 2.0 (2023) с новыми Django несовместим. |
| crispy-bootstrap3 | 2022.1 | **2024.1** | 2022.1 заявляет поддержку только до Django 4.1. |
| crispy-bootstrap5 | 0.7 | **2026.9** | 0.7 (2022); актуальная версия требует Django ≥ 5.2. В проекте закомментирован (`config/settings.py`, строка 20). |
| django-filter | 22.1 | **26.2** | 26.2 требует Django ≥ 5.2 и Python ≥ 3.11. В проекте нигде не используется. |
| djangorestframework | 3.14.0 | **3.18.3** | 3.18.3 требует Django ≥ 5.2 и Python ≥ 3.10. |
| asgiref | 3.6.0 | **3.13.0** | Django 6.1 требует asgiref ≥ 3.9.1; 3.6.0 не подойдёт. |
| sqlparse | 0.4.3 | **0.6.0** | Django 6.1 требует sqlparse ≥ 0.5.0. |
| pytz | 2022.7.1 | **2026.6** | Пакет объявлен **deprecated** («fails for dates starting 2038», см. README пакета на PyPI). Для Python 3.9+ рекомендуется `zoneinfo` + `tzdata`. Новые Django его не требуют. |
| black | 23.1.0 | **26.10.1** | Старые версии ломаются на новых Python (транзитивные click/pathspec); актуальная требует Python ≥ 3.10. |
| isort | 5.12.0 | **9.0.2** | Актуальная требует Python ≥ 3.10. |
| click | 8.1.3 | **8.5.0** | Транзитивная зависимость black. |
| mypy-extensions | 1.0.0 | **1.1.0** | Транзитивная. |
| packaging | 23.0 | **26.3** | Транзитивная. |
| pathspec | 0.11.0 | **1.1.1** | Транзитивная (black). |
| platformdirs | 3.0.0 | **4.14.0** | Транзитивная (black); актуальная требует Python ≥ 3.11. |
| tomli | 2.0.1 | **2.5.0** | **Не нужен** на Python ≥ 3.11 (в stdlib есть `tomllib`, PEP 680). На Python 3.14 — мёртвый груз. |

### 2.2. Окружение (`.venv`)

| Компонент | Версия | Актуальная | Файл-источник |
|---|---|---|---|
| Python | 3.14.4 | 3.14.x (актуальная ветка) | `.venv/pyvenv.cfg`, строка 3 |
| pip | 25.1.1 | 26.2.2 | `.venv/lib/python3.14/site-packages/pip-25.1.1.dist-info/METADATA` |
| Django и остальные зависимости | **не установлены** | — | в `.venv` присутствует только pip |

### 2.3. Frontend-зависимости (`todo/templates/todo/base.html`)

| Библиотека | Версия в проекте | Комментарий |
|---|---|---|
| Bootstrap | 5.1.3 (локально, `todo/static/todo/css/bootstrap.min.css`, строка 2) | Устарел (2021); актуальна ветка 5.3.x. |
| jQuery | 3.3.1 slim (CDN, строка 12) | Устарел; актуальна ветка 3.7.x. |
| Popper.js | 1.14.6 (CDN, строка 13) | **Несовместим:** Bootstrap 5 требует Popper 2.x (`@popperjs/core`); выпадающие компоненты BS5 работать не будут. |
| Font Awesome | 4.7.0 (CDN, строка 16) | Устарел; актуальна ветка 6.x. |
| Moment.js | 2.23.0 (CDN, строка 19) | Проект в maintenance-режиме; в коде не используется. |
| Tempus Dominus | 5.1.2 **Bootstrap 4** (CDN, строки 22–23) | Вариант для Bootstrap 4, а в проекте Bootstrap 5; инициализация ссылается на несуществующий `#datetimepicker1` (`base.html`, строки 55–61). |

---

## 3. Совместимость с современным Python и Django

### 3.1. Матрица совместимости Django/Python

| Django | Поддержка Python | Статус |
|---|---|---|
| 4.1 (в проекте) | 3.8–3.11 | EOL с декабря 2023 |
| 4.2 LTS | 3.8–3.12 | EOL в апреле 2026 |
| 5.2 LTS | 3.10–3.13 | поддерживается до апреля 2028 |
| 6.1 (актуальная) | 3.12–3.14 | поддерживается |

### 3.2. Конкретные проблемы несовместимости

1. **Django 4.1.7 не работает на Python 3.12+.** Официальный диапазон 4.1 — Python 3.8–3.11. На Python 3.12 Django < 4.2.8 падает при запуске из-за удалённого из stdlib `pkgutil.ImpImporter` (поддержка Python 3.12 появилась в Django 4.2.8 / 5.0.1). В `.venv` стоит Python 3.14.4 — гарантированная неработоспособность.
2. **Несовместимые с новым Django сопутствующие пакеты:** при переходе на Django 5.2/6.x потребуются: django-crispy-forms ≥ 2.3 (актуально 2.7), crispy-bootstrap5 2026.x, django-filter ≥ 26.x, DRF ≥ 3.18, asgiref ≥ 3.9.1, sqlparse ≥ 0.5.0. Текущие версии из `requirements.txt` несовместимы (см. таблицу 2.1).
3. **pytz 2022.7.1** — deprecated и не держит даты после 2038; при апгрейде Django заменяется на `zoneinfo`/`tzdata` (для Windows, где зонная база берётся из `tzdata`).
4. **tomli 2.0.1** — на Python 3.14 не нужен (`tomllib` в stdlib); остался от Python < 3.11.
5. **Инструменты разработки:** black 23.1.0 / isort 5.12.0 / platformdirs 3.0.0 / pathspec 0.11.0 рассчитаны на Python 3.7–3.11 и на Python 3.13/3.14 могут не запускаться (в т.ч. через устаревшие транзитивные click 8.1.3 и platformdirs 3.0.0).
6. **Bootstrap 5.1.3 + Popper 1.14.6** — Popper 1.x несовместим с Bootstrap 5 (требуется Popper 2.x); интерактивные компоненты (dropdown и т.п.) не работают (`base.html`, строки 10–13).

---

## 4. Проблемы конфигурации (`config/settings.py`)

| # | Проблема | Файл:строки | Критичность |
|---|---|---|---|
| 4.1 | `SECRET_KEY = ""` — пустой секретный ключ; ломает подпись сессий/CSRF и критичен для production. | `config/settings.py:4` | Критично |
| 4.2 | `DEBUG = True` захардкожен; утечка отладочной информации и stack traces в production. | `config/settings.py:6` | Критично |
| 4.3 | `ALLOWED_HOSTS = []` — в production приложение не будет принимать запросы ни с каких хостов (кроме localhost в DEBUG). | `config/settings.py:8` | Критично |
| 4.4 | `REST_FRAMEWORK = {...}` задан, но `rest_framework` **отсутствует** в `INSTALLED_APPS` и API-маршрутов нет — конфиг мёртвый. | `config/settings.py:28-32` против `:11-23`; `config/urls.py:4` | Средняя |
| 4.5 | `django_filters` подключён в `INSTALLED_APPS`, но нигде не используется (нет ни одного `FilterSet`). | `config/settings.py:22` | Низкая |
| 4.6 | `crispy_bootstrap5` закомментирован, хотя пакет есть в `requirements.txt`; активен `crispy_bootstrap3`, при том что разметка использует Bootstrap 5.1.3. | `config/settings.py:20-21`, `:25-26`; `todo/templates/todo/base.html:10` | Средняя |
| 4.7 | `CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap3"` — строка вместо списка; работает только потому, что проверка «вхождения» совпадает. | `config/settings.py:25` | Низкая |
| 4.8 | `STATIC_URL = "static/"` без ведущего слэша (рекомендация Django — `/static/`); отсутствуют `STATICFILES_DIRS`/`STATIC_ROOT` — для production статика не соберётся. | `config/settings.py:95` | Средняя |
| 4.9 | Нет вынесения настроек в переменные окружения (SECRET_KEY/DEBUG/ALLOWED_HOSTS захардкожены); `.gitignore` предусматривает `.env` (строки 14–16), но механизма чтения нет. | `config/settings.py:4-8`; `.gitignore:14-16` | Средняя |
| 4.10 | `django.contrib.sessions` и `django.contrib.messages` включены, но не используются (в шаблонах нет вывода messages, аутентификации нет) — избыточность. | `config/settings.py:14,16` | Низкая |
| 4.11 | `config/asgi.py` объявлен для синхронного приложения — работоспособно, но избыточно. | `config/asgi.py` | Низкая |

---

## 5. Проблемы миграций (`todo/migrations/`)

| # | Проблема | Файл:строки | Критичность |
|---|---|---|---|
| 5.1 | **Потеря данных:** `0003_rename_tasks.py` создаёт новую модель `Tasks` и **удаляет** `Item` (`DeleteModel`) без переноса данных (`RunPython` отсутствует). | `todo/migrations/0003_rename_tasks.py:11-52` | Критично |
| 5.2 | **Инверсия семантики между миграциями:** `is_done` имел `default=False` (0001), а `is_active` получил `default=True` (0003) — даже перенос данных дал бы противоположные статусы. | `todo/migrations/0001_add_item.py:28`; `0003_rename_tasks.py:30` | Критично |
| 5.3 | Заголовки миграций и `manage.py` ссылаются на несуществующий фреймворк **«DjangoOld»** — артефакт переименованного Django; миграции не перегенерированы под обычный Django, текст ошибки в `manage.py` вводит в заблуждение. | `todo/migrations/0002_rename_is_active.py:1`; `0003_rename_tasks.py:1`; `manage.py:2,14` | Низкая |
| 5.4 | Имя файла `0003_rename_tasks.py` не отражает содержимое (там `CreateModel` + `DeleteModel`, а не `RenameModel`). | `todo/migrations/0003_rename_tasks.py` | Низкая |
| 5.5 | В модели `Tasks` нет `__str__` — в админке (хлебные крошки, select-поля, история) объекты показываются как «Tasks object (1)». | `todo/models.py:4-16` | Низкая |
| 5.6 | Косметика: висячий пробел `), ` в 0001; файл БД `db.sqlite3` отсутствует — схему надо создавать `migrate`. | `todo/migrations/0001_add_item.py:20`; `.gitignore:11` | Низкая |

---

## 6. Неиспользуемые приложения и настройки

| Объект | Где объявлен | Статус использования |
|---|---|---|
| `REST_FRAMEWORK` (пагинация `LimitOffsetPagination`, `PAGE_SIZE=2`, фильтр-бэкенд) | `config/settings.py:28-32` | Мёртвый: `rest_framework` не в `INSTALLED_APPS`, API-маршрутов нет. |
| `django_filters` | `config/settings.py:22` | Мёртвый: нет ни одного `FilterSet`; DRF-бэкенд ссылается на несуществующий DRF. |
| `crispy_bootstrap5` | `requirements.txt:5`; закомментирован в `config/settings.py:20` | Установлен в requirements, но не используется. |
| `pytz` | `requirements.txt:15` | Транзитивная для старых Django; при апгрейде — удалить. |
| `tomli` | `requirements.txt:17` | Не нужен на Python ≥ 3.11. |
| jQuery (кроме `submit()`), Popper, Font Awesome, Moment.js, Tempus Dominus | `todo/templates/todo/base.html:12-23` | Подключены, но не используются; datetimepicker инициализируется для отсутствующего элемента `#datetimepicker1` (`base.html:55-61`). |
| `sticky-footer-navbar.css` | `todo/static/todo/css/sticky-footer-navbar.css` | Используется (`base.html:11`) — единственный собственный стиль (1 правило). |
| `django.contrib.sessions` / `messages` | `config/settings.py:14,16` | Пользовательской аутентификации и вывода сообщений нет. |

---

## 7. Окружение и документация

1. **Виртуальное окружение пустое:** `.venv/pyvenv.cfg` — Python 3.14.4; из пакетов установлен только pip 25.1.1. `python manage.py runserver` не запустится (Django не установлен, а при установке из `requirements.txt` — несовместим с Python 3.14).
2. **`README.md` содержит неточные инструкции:** имена пакетов не совпадают с именами на PyPI (`crispy_bootstrap3` → `crispy-bootstrap3`, `django_filter` → `django-filter`), версии не зафиксированы, `django-crispy-forms`/`crispy-bootstrap5` ставятся, но не используются в конфигурации. | `README.md:1-9`
3. **`requirements.txt` закрепляет устаревший набор целиком** (`==` для всех пакетов) без разделения на runtime/dev-зависимости; black/isort/mypy-extensions — инструменты разработки, попавшие в рантайм-список. | `requirements.txt:1-17`
4. **`.gitignore` корректен** (`.venv/`, `db.sqlite3`, `.env` и секреты исключены). | `.gitignore:1-18`

---

## 8. Сводная таблица приоритетов

### Критично (блокирует запуск/потеря данных)

1. Стек несовместим с Python 3.14.4 в `.venv` (Django 4.1.7 + устаревшие пакеты) — приложение не запускается (§3.2, п.1–2; §7, п.1).
2. Django 4.1.7 EOL с 12.2023 — нет security-обновлений (§2.1).
3. Пустой `SECRET_KEY`, `DEBUG=True`, `ALLOWED_HOSTS=[]` (§4.1–4.3).
4. Миграция `0003` удаляет таблицу `Item` без переноса данных; между миграциями инвертирована семантика флага (§5.1–5.2).

### Высокий

5. Несовместимые с актуальным Django версии crispy-forms/django-filter/DRF/asgiref/sqlparse при будущем апгрейде (§2.1).
6. Мёртвая конфигурация `REST_FRAMEWORK` без DRF в `INSTALLED_APPS` (§4.4).
7. crispy `bootstrap3` против Bootstrap 5.1.3 в разметке; Popper 1.x при Bootstrap 5 (§2.3, §4.6).
8. Отсутствие `STATICFILES_DIRS`/`STATIC_ROOT` и настроек из переменных окружения (§4.8–4.9).

### Средний

9. Неиспользуемые зависимости (django-filter, pytz, tomli, CDN-библиотеки) (§6).
10. `CRISPY_ALLOWED_TEMPLATE_PACKS` строкой; `STATIC_URL` без слэша (§4.7–4.8).
11. `.venv` с pip 25.1.1 и без зависимостей; `README.md` с неверными именами пакетов (§7.1–7.2).

### Низкий

12. Заголовки «DjangoOld» в миграциях и `manage.py` (§5.3).
13. Отсутствие `__str__` у модели; висячий пробел в миграции 0001 (§5.5–5.6).
14. Избыточные `sessions`/`messages`/`asgi.py` (§4.10–4.11).