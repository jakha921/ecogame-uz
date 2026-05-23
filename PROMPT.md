# EcoGame — Экологическая игра-симулятор экосистемы (на узбекском языке)

> **Автор:** Рузибаев Жахонгир Дилмуратович (036-21 SMMr)
> **Тема:** Разработка экологической игры по охране окружающей среды
> **Научные руководители:** Узакова М.А., Абидова Ш.Б.
> **Стек:** Django REST + React 19 + Phaser.js + Docker + Coolify
> **Домен:** https://ecogame.fullfocus.dev
>
> **Команда запуска ralph-loop:**
> ```
> /ralph-loop:ralph-loop "Прочитай PROMPT.md (/Users/jakha/MyFiles/University/Diploma/PROMPT.md). Найди первую незавершённую задачу [ ]. Выполни её полностью — создай файлы, напиши код, запусти проверку (uv run python manage.py check для бэкенда, npm run build для фронтенда). Отметь [x] в PROMPT.md. Закоммить изменения. Повторяй до ALL PHASES COMPLETE." --max-iterations 70 --completion-promise "ALL PHASES COMPLETE" /compact /senior-qa /senior-backend /senior-frontend /frontend-design:frontend-design /server-advisor
> ```

---

## Phase 1: Инициализация проекта и конфигурация

### [x] 1.1 Инициализировать Git-репозиторий и базовые файлы

**Что сделать:**
- Выполнить `git init` в `/Users/jakha/MyFiles/University/Diploma/`
- Создать `.gitignore` с правилами для Python, Node.js, Docker, IDE, секретов:
  - Python: `__pycache__/`, `*.pyc`, `.venv/`, `*.egg-info/`, `.pytest_cache/`, `.ruff_cache/`, `htmlcov/`, `.coverage`
  - Node: `node_modules/`, `dist/`, `.vite/`, `*.local`
  - Docker: `.env`, `.env.local`, `.env.*.local`
  - IDE: `.vscode/`, `.idea/`, `*.swp`, `.DS_Store`
  - DB: `*.sqlite3`, `db.sqlite3`
  - Media: `backend/media/`, `backend/static_collected/`
- Создать `README.md` с описанием проекта на русском:
  - Название, описание, стек технологий
  - Инструкции запуска dev: `docker compose -f docker-compose.dev.yml up`
  - Инструкции запуска prod: `docker compose up`
  - URL: https://ecogame.fullfocus.dev
- Создать `.env.example`:
  ```
  # Django
  DJANGO_SECRET_KEY=change-me-in-production-use-50-char-random-string
  DJANGO_DEBUG=True
  DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
  DATABASE_URL=sqlite:///db.sqlite3

  # PostgreSQL (production only)
  POSTGRES_DB=ecogame
  POSTGRES_USER=ecogame
  POSTGRES_PASSWORD=change-me-strong-password

  # CORS
  CORS_ALLOWED_ORIGINS=http://localhost:3000

  # Frontend
  VITE_API_URL=http://localhost:8000/api/v1
  ```
- Создать структуру каталогов командой mkdir:
  - `backend/`
  - `frontend/`
  - `nginx/`
  - `docs/vkr/`
  - `docs/presentation/`

**Проверка:** `git status` показывает файлы, `ls -la` показывает все директории.
**Коммит:** `chore: инициализировать репозиторий и базовые конфигурации`

---

### [x] 1.2 Настроить Django-проект (backend)

**Что сделать:**
- В директории `backend/` инициализировать uv-проект:
  ```bash
  cd backend && uv init --no-readme
  ```
- Настроить `pyproject.toml` — добавить в секцию `[project].dependencies`:
  - `django>=5.1`
  - `djangorestframework>=3.15`
  - `django-unfold>=0.40`
  - `djangorestframework-simplejwt>=5.3`
  - `django-cors-headers>=4.4`
  - `django-environ>=0.11`
  - `gunicorn>=22.0`
  - `psycopg2-binary>=2.9`
  - `Pillow>=10.4`
  - В `[tool.uv.dev-dependencies]`: `pytest>=8`, `pytest-django>=4.8`, `ruff>=0.6`
- Выполнить `uv sync`
- Создать Django-проект: `uv run django-admin startproject config .`
- Создать директорию `config/settings/` и переместить `settings.py` → `config/settings/base.py`
- Создать `config/settings/__init__.py` (пустой)
- Создать `config/settings/dev.py`:
  ```python
  from .base import *
  DEBUG = True
  DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
  CORS_ALLOW_ALL_ORIGINS = True
  ```
- Создать `config/settings/prod.py`:
  ```python
  import environ
  from .base import *
  env = environ.Env()
  DEBUG = False
  SECRET_KEY = env("DJANGO_SECRET_KEY")
  ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
  DATABASES = {"default": env.db("DATABASE_URL")}
  CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")
  STATIC_ROOT = BASE_DIR / "static_collected"
  SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
  ```
- В `config/settings/base.py` добавить:
  - `INSTALLED_APPS`: `rest_framework`, `rest_framework_simplejwt`, `corsheaders`, `unfold` (перед `django.contrib.admin`)
  - `MIDDLEWARE`: `corsheaders.middleware.CorsMiddleware` (первым)
  - `REST_FRAMEWORK` конфиг:
    ```python
    REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 20,
    }
    ```
  - `SIMPLE_JWT`: `ACCESS_TOKEN_LIFETIME = timedelta(hours=1)`, `REFRESH_TOKEN_LIFETIME = timedelta(days=7)`
  - `STATIC_URL = "/static/"`, `MEDIA_URL = "/media/"`, `MEDIA_ROOT = BASE_DIR / "media"`
- Обновить `manage.py`: `os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")`
- Создать `config/urls.py` (заготовка с admin и api/v1/ prefix)
- Создать `pytest.ini` в `backend/`:
  ```ini
  [pytest]
  DJANGO_SETTINGS_MODULE = config.settings.dev
  python_files = test_*.py tests.py
  ```

**Проверка:** `cd backend && uv run python manage.py check` — без ошибок.
**Коммит:** `chore: настроить Django-проект с split settings`

---

### [x] 1.3 Настроить React-проект (frontend)

**Что сделать:**
- В директории `frontend/` создать проект:
  ```bash
  cd frontend && npm create vite@latest . -- --template react-ts
  ```
- Установить зависимости одной командой:
  ```bash
  npm install phaser@^3.80 zustand@^5 react-router-dom@^7 axios@^1.7 zod@^3.23 react-hook-form@^7.53 @hookform/resolvers@^3.9 react-hot-toast@^2.4 clsx@^2.1
  npm install -D tailwindcss@^4 @tailwindcss/vite prettier @types/node
  ```
- Настроить `tsconfig.json`:
  - `"strict": true`
  - `"baseUrl": "."`, `"paths": {"@/*": ["src/*"]}`
  - `"noUnusedLocals": true`, `"noUnusedParameters": true`
- Настроить `vite.config.ts`:
  ```typescript
  import { defineConfig } from "vite";
  import react from "@vitejs/plugin-react";
  import tailwindcss from "@tailwindcss/vite";
  import path from "path";

  export default defineConfig({
    plugins: [react(), tailwindcss()],
    resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
    server: {
      proxy: {
        "/api": { target: "http://localhost:8000", changeOrigin: true },
        "/admin": { target: "http://localhost:8000", changeOrigin: true },
      },
    },
  });
  ```
- Создать `.prettierrc`:
  ```json
  { "semi": true, "singleQuote": false, "tabWidth": 2, "trailingComma": "es5" }
  ```
- Создать пустые директории в `src/`:
  - `api/`, `stores/`, `pages/`, `components/`, `game/events/`, `game/scenes/`, `game/objects/`, `game/systems/`, `game/data/`, `hooks/`, `i18n/`, `styles/`
- Обновить `src/main.tsx` с базовым Tailwind импортом
- Обновить `src/styles/globals.css` с Tailwind директивами

**Проверка:** `cd frontend && npm run build` — успешная сборка без TypeScript ошибок.
**Коммит:** `chore: настроить React + TypeScript + Vite + Phaser проект`

---

### [x] 1.4 Создать Docker-конфигурацию для разработки

**Что сделать:**
- Создать `backend/Dockerfile`:
  ```dockerfile
  FROM python:3.12-slim
  ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
  WORKDIR /app
  COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
  COPY pyproject.toml uv.lock* ./
  RUN uv sync --frozen
  COPY . .
  EXPOSE 8000
  CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
  ```
- Создать `frontend/Dockerfile`:
  ```dockerfile
  FROM node:20-alpine
  WORKDIR /app
  COPY package.json package-lock.json* ./
  RUN npm ci
  COPY . .
  EXPOSE 3000
  CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
  ```
- Создать `docker-compose.dev.yml`:
  ```yaml
  services:
    backend:
      build: ./backend
      volumes:
        - ./backend:/app
        - /app/.venv
      ports:
        - "8000:8000"
      env_file: .env
      environment:
        - DJANGO_SETTINGS_MODULE=config.settings.dev

    frontend:
      build: ./frontend
      volumes:
        - ./frontend:/app
        - /app/node_modules
      ports:
        - "3000:3000"
      env_file: .env
      depends_on:
        - backend
  ```
- Создать `.env` из `.env.example` (для локальной разработки, НЕ коммитить):
  - Скопировать `.env.example` → `.env`, заменить значения на рабочие
- Создать `CLAUDE.md` в корне проекта:
  ```markdown
  # EcoGame — Project-specific Claude Instructions

  ## Команды проверки
  - Backend: `cd backend && uv run python manage.py check`
  - Backend tests: `cd backend && uv run pytest -v`
  - Backend lint: `cd backend && uv run ruff check --fix .`
  - Frontend: `cd frontend && npm run build`
  - Frontend lint: `cd frontend && npm run lint`
  - Docker dev: `docker compose -f docker-compose.dev.yml up --build`

  ## Контент
  - ВСЕ пользовательские тексты в игре — на узбекском языке (латиница)
  - Поля с узбекским контентом именуются с суффиксом `_uz`
  - Текст ВКР — на русском языке

  ## Структура
  - Backend: `backend/apps/` — Django приложения
  - Frontend: `frontend/src/` — React + Phaser код
  - Docs: `docs/vkr/` — текст диплома, `docs/presentation/` — презентация
  ```

**Проверка:** `docker compose -f docker-compose.dev.yml config` — валидная конфигурация (нет ошибок).
**Коммит:** `chore: добавить Docker конфигурацию для разработки`

---

## Phase 2: Модели базы данных и админ-панель

### [x] 2.1 Создать приложение accounts с моделью Player

**Что сделать:**
- Создать директорию `backend/apps/` и файл `backend/apps/__init__.py`
- Создать приложение: `cd backend && uv run python manage.py startapp accounts apps/accounts`
- Создать `apps/accounts/models.py`:
  ```python
  from django.contrib.auth.models import AbstractUser
  from django.db import models

  class Player(AbstractUser):
      """Расширенная модель игрока с игровыми данными."""
      nickname = models.CharField(max_length=50, unique=True, verbose_name="Ник")
      avatar = models.CharField(max_length=50, default="default", verbose_name="Аватар")
      total_score = models.PositiveIntegerField(default=0, verbose_name="Общий счёт")

      class Meta:
          verbose_name = "Игрок"
          verbose_name_plural = "Игроки"
          ordering = ["-total_score"]

      def __str__(self) -> str:
          return self.nickname or self.username
  ```
- В `config/settings/base.py` добавить:
  - `AUTH_USER_MODEL = "accounts.Player"`
  - `"apps.accounts"` в INSTALLED_APPS
  - В UNFOLD config добавить `"django.contrib.auth"` переопределение
- В `apps/accounts/apps.py` изменить `name = "apps.accounts"`
- Создать `apps/accounts/admin.py`:
  ```python
  from unfold.admin import ModelAdmin
  from django.contrib import admin
  from .models import Player

  @admin.register(Player)
  class PlayerAdmin(ModelAdmin):
      list_display = ["username", "nickname", "email", "total_score", "date_joined", "is_active"]
      list_filter = ["is_active", "date_joined"]
      search_fields = ["username", "nickname", "email"]
      ordering = ["-total_score"]
  ```
- Создать миграции: `uv run python manage.py makemigrations accounts`
- Применить: `uv run python manage.py migrate`

**Проверка:** `uv run python manage.py check` без ошибок, миграция применена.
**Коммит:** `feat: добавить модель Player (кастомный пользователь)`

---

### [x] 2.2 Создать модели игровой логики (Level, EcoAction, GameSession, GameProgress, ActionLog)

**Что сделать:**
- Создать приложение: `uv run python manage.py startapp game apps/game`
- В `apps/game/apps.py` — `name = "apps.game"`
- Добавить `"apps.game"` в INSTALLED_APPS
- Создать `apps/game/models.py` со следующими моделями (все с type hints, verbose_name, ordering, __str__):

  **Level:**
  ```python
  class Level(models.Model):
      number = models.PositiveSmallIntegerField(unique=True, verbose_name="Номер")
      name_uz = models.CharField(max_length=100, verbose_name="Название (уз)")
      description_uz = models.TextField(verbose_name="Описание (уз)")
      required_score = models.PositiveIntegerField(default=0, verbose_name="Очков для разблокировки")
      map_config = models.JSONField(default=dict, verbose_name="Конфигурация карты")
      ecosystem_initial = models.JSONField(default=dict, verbose_name="Начальные индикаторы")
      # ecosystem_initial пример: {"air": 30, "water": 25, "soil": 20, "biodiversity": 15}

      class Meta:
          verbose_name = "Уровень"
          verbose_name_plural = "Уровни"
          ordering = ["number"]

      def __str__(self) -> str:
          return f"Level {self.number}: {self.name_uz}"
  ```

  **EcoAction:**
  ```python
  class ActionCategory(models.TextChoices):
      FLORA = "FLORA", "Флора"
      WATER = "WATER", "Вода"
      WASTE = "WASTE", "Отходы"
      ENERGY = "ENERGY", "Энергия"
      FAUNA = "FAUNA", "Фауна"

  class EcoAction(models.Model):
      key = models.CharField(max_length=50, unique=True)
      name_uz = models.CharField(max_length=100)
      description_uz = models.TextField()
      category = models.CharField(max_length=10, choices=ActionCategory.choices)
      score_value = models.PositiveIntegerField(default=10)
      air_impact = models.FloatField(default=0.0)
      water_impact = models.FloatField(default=0.0)
      soil_impact = models.FloatField(default=0.0)
      biodiversity_impact = models.FloatField(default=0.0)
      cooldown_seconds = models.PositiveIntegerField(default=5)
      unlock_level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="actions")
      sprite_key = models.CharField(max_length=50, default="default")
      # ... Meta, __str__
  ```

  **GameSession:**
  ```python
  class GameSession(models.Model):
      player = models.ForeignKey("accounts.Player", on_delete=models.CASCADE, related_name="sessions")
      level = models.ForeignKey(Level, on_delete=models.CASCADE)
      started_at = models.DateTimeField(auto_now_add=True)
      ended_at = models.DateTimeField(null=True, blank=True)
      is_active = models.BooleanField(default=True)
      # Meta, __str__
  ```

  **GameProgress:**
  ```python
  class GameProgress(models.Model):
      player = models.ForeignKey("accounts.Player", on_delete=models.CASCADE, related_name="progress")
      level = models.ForeignKey(Level, on_delete=models.CASCADE)
      score = models.PositiveIntegerField(default=0)
      air_quality = models.FloatField(default=0.0)
      water_purity = models.FloatField(default=0.0)
      soil_health = models.FloatField(default=0.0)
      biodiversity = models.FloatField(default=0.0)
      actions_performed = models.JSONField(default=dict)
      completed = models.BooleanField(default=False)
      completed_at = models.DateTimeField(null=True, blank=True)
      updated_at = models.DateTimeField(auto_now=True)

      class Meta:
          unique_together = ("player", "level")
          # ...
  ```

  **ActionLog:**
  ```python
  class ActionLog(models.Model):
      session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name="action_logs")
      action = models.ForeignKey(EcoAction, on_delete=models.CASCADE)
      performed_at = models.DateTimeField(auto_now_add=True)
      position_x = models.FloatField(default=0)
      position_y = models.FloatField(default=0)
      result_delta = models.JSONField(default=dict)
      # Meta, __str__
  ```

- Создать миграции и применить

**Проверка:** `uv run python manage.py makemigrations game && uv run python manage.py migrate && uv run python manage.py check`
**Коммит:** `feat: добавить модели Level, EcoAction, GameSession, GameProgress, ActionLog`

---

### [x] 2.3 Создать модели Achievement, Education, Leaderboard

**Что сделать:**
- В `apps/game/models.py` добавить:
  ```python
  class ConditionType(models.TextChoices):
      SCORE = "SCORE", "Очки"
      ACTION_COUNT = "ACTION_COUNT", "Количество действий"
      LEVEL_COMPLETE = "LEVEL_COMPLETE", "Завершение уровня"
      INDICATOR = "INDICATOR", "Индикатор"

  class Achievement(models.Model):
      key = models.CharField(max_length=50, unique=True)
      name_uz = models.CharField(max_length=100)
      description_uz = models.TextField()
      icon = models.CharField(max_length=50, default="star")
      condition_type = models.CharField(max_length=20, choices=ConditionType.choices)
      condition_value = models.JSONField(default=dict)
      # condition_value примеры:
      # ACTION_COUNT: {"action_key": "plant_tree", "count": 10}
      # SCORE: {"min_score": 1000}
      # LEVEL_COMPLETE: {"level_number": 1}
      # INDICATOR: {"indicator": "air", "min_value": 80}

  class PlayerAchievement(models.Model):
      player = models.ForeignKey("accounts.Player", on_delete=models.CASCADE, related_name="achievements")
      achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
      unlocked_at = models.DateTimeField(auto_now_add=True)

      class Meta:
          unique_together = ("player", "achievement")
  ```

- Создать приложение education: `uv run python manage.py startapp education apps/education`
- В `apps/education/models.py`:
  ```python
  class EducationalContent(models.Model):
      title_uz = models.CharField(max_length=200)
      body_uz = models.TextField()
      category = models.CharField(max_length=10, choices=ActionCategory.choices)
      image = models.ImageField(upload_to="education/", blank=True)
      order = models.PositiveSmallIntegerField(default=0)
      is_published = models.BooleanField(default=True)
      created_at = models.DateTimeField(auto_now_add=True)
      # Meta: ordering = ["order"], __str__

  class EcoFact(models.Model):
      text_uz = models.CharField(max_length=300)
      source = models.CharField(max_length=200, blank=True)
      category = models.CharField(max_length=10, choices=ActionCategory.choices)
      # __str__
  ```
  - Импортировать `ActionCategory` из `apps.game.models`

- Создать приложение leaderboard: `uv run python manage.py startapp leaderboard apps/leaderboard`
- В `apps/leaderboard/models.py`:
  ```python
  class LeaderboardEntry(models.Model):
      player = models.OneToOneField("accounts.Player", on_delete=models.CASCADE, related_name="leaderboard_entry")
      total_score = models.PositiveIntegerField(default=0)
      levels_completed = models.PositiveSmallIntegerField(default=0)
      achievements_count = models.PositiveSmallIntegerField(default=0)
      rank = models.PositiveIntegerField(default=0, db_index=True)
      updated_at = models.DateTimeField(auto_now=True)
      # Meta: ordering = ["rank"], __str__
  ```

- Добавить все три новых приложения в INSTALLED_APPS
- Создать и применить миграции

**Проверка:** `uv run python manage.py makemigrations && uv run python manage.py migrate && uv run python manage.py check`
**Коммит:** `feat: добавить модели Achievement, EducationalContent, EcoFact, LeaderboardEntry`

---

### [x] 2.4 Настроить Unfold Admin для всех моделей

**Что сделать:**
- В `config/settings/base.py` настроить Unfold:
  ```python
  UNFOLD = {
      "SITE_TITLE": "EcoGame Admin",
      "SITE_HEADER": "EcoGame — Boshqaruv paneli",
      "SITE_URL": "/",
      "COLORS": {
          "primary": {"50": "240 253 244", "500": "34 197 94", "900": "20 83 45"},
      },
  }
  ```
- Создать `apps/game/admin.py` с регистрацией Level, EcoAction, GameSession, GameProgress, ActionLog, Achievement, PlayerAchievement через `unfold.admin.ModelAdmin`:
  - Level: list_display=[number, name_uz, required_score], list_filter=[number]
  - EcoAction: list_display=[key, name_uz, category, score_value], list_filter=[category]
  - GameProgress: list_display=[player, level, score, completed], list_filter=[completed]
  - Achievement: list_display=[key, name_uz, condition_type]
- Создать `apps/education/admin.py`:
  - EducationalContent: list_display=[title_uz, category, is_published, order], list_editable=[order, is_published]
  - EcoFact: list_display=[text_uz, category]
- Создать `apps/leaderboard/admin.py`:
  - LeaderboardEntry: list_display=[player, total_score, rank, levels_completed]

**Проверка:** Запустить сервер, войти в http://localhost:8000/admin/ — видна Unfold-панель со всеми моделями.
**Коммит:** `feat: настроить Unfold Admin для всех моделей`

---

### [x] 2.5 Создать фикстуры с контентом на узбекском языке

**Что сделать:**
- Создать `backend/fixtures/` директорию
- Создать `backend/fixtures/levels.json` — 4 уровня:
  ```json
  [
    {"model": "game.level", "pk": 1, "fields": {
      "number": 1,
      "name_uz": "Kichik hovli",
      "description_uz": "O'z hovlingizni yashil va toza qiling. Daraxt turing, gullar oching, chiqindilarni tozalang.",
      "required_score": 0,
      "map_config": {"width": 20, "height": 15, "zones": [{"type": "FLORA", "x": 5, "y": 5}, {"type": "WATER", "x": 15, "y": 8}, {"type": "WASTE", "x": 10, "y": 12}, {"type": "ENERGY", "x": 3, "y": 10}]},
      "ecosystem_initial": {"air": 30, "water": 25, "soil": 20, "biodiversity": 15}
    }},
    {"model": "game.level", "pk": 2, "fields": {
      "number": 2,
      "name_uz": "Mahalla",
      "description_uz": "Mahallangizni ekologik toza qiling. Ko'proq daraxt o'tqazing, ariqlarni tozalang.",
      "required_score": 500,
      "map_config": {"width": 30, "height": 20, "zones": [{"type": "FLORA", "x": 8, "y": 5}, {"type": "FLORA", "x": 22, "y": 10}, {"type": "WATER", "x": 15, "y": 15}, {"type": "WASTE", "x": 5, "y": 18}, {"type": "WASTE", "x": 25, "y": 3}, {"type": "ENERGY", "x": 20, "y": 18}, {"type": "FAUNA", "x": 10, "y": 10}]},
      "ecosystem_initial": {"air": 25, "water": 20, "soil": 15, "biodiversity": 10}
    }},
    {"model": "game.level", "pk": 3, "fields": {
      "number": 3,
      "name_uz": "Shahar",
      "description_uz": "Shahar ekologiyasini yaxshilang. Sanoat korxonalari ifloslanishga qarshi kurashing.",
      "required_score": 1500,
      "map_config": {"width": 40, "height": 25},
      "ecosystem_initial": {"air": 15, "water": 15, "soil": 10, "biodiversity": 8}
    }},
    {"model": "game.level", "pk": 4, "fields": {
      "number": 4,
      "name_uz": "Viloyat",
      "description_uz": "Butun viloyat ekologiyasini tiklang. Orol dengizi kabi muammolarga qarshi kurashing.",
      "required_score": 3000,
      "map_config": {"width": 50, "height": 30},
      "ecosystem_initial": {"air": 10, "water": 10, "soil": 8, "biodiversity": 5}
    }}
  ]
  ```

- Создать `backend/fixtures/eco_actions.json` — 12 действий (все с `unlock_level` FK):
  - plant_tree (FLORA, air_impact: 1.5, biodiversity_impact: 1.2, score: 20)
  - plant_flowers (FLORA, biodiversity_impact: 0.8, score: 10)
  - care_garden (FLORA, soil_impact: 1.0, biodiversity_impact: 0.5, score: 15)
  - clean_water (WATER, water_impact: 2.0, biodiversity_impact: 1.0, score: 25)
  - save_water (WATER, water_impact: 0.8, score: 10)
  - sort_waste (WASTE, soil_impact: 1.5, score: 20)
  - recycle (WASTE, soil_impact: 1.0, air_impact: 0.5, score: 15)
  - install_solar (ENERGY, air_impact: 2.0, score: 30, unlock_level: 2)
  - save_energy (ENERGY, air_impact: 0.8, score: 10)
  - protect_animal (FAUNA, biodiversity_impact: 2.5, score: 30, unlock_level: 2)
  - bird_house (FAUNA, biodiversity_impact: 1.5, score: 20)
  - save_fish (FAUNA, water_impact: 1.2, biodiversity_impact: 1.8, score: 25, unlock_level: 3)

- Создать `backend/fixtures/achievements.json` — 10 достижений
- Создать `backend/fixtures/educational_content.json` — 5 статей на узбекском
- Создать `backend/fixtures/eco_facts.json` — 15 фактов на узбекском

- Загрузить фикстуры:
  ```bash
  uv run python manage.py loaddata fixtures/levels.json fixtures/eco_actions.json fixtures/achievements.json fixtures/educational_content.json fixtures/eco_facts.json
  ```

**Проверка:** Данные видны в Django Admin (уровни, действия, достижения).
**Коммит:** `feat: добавить фикстуры с узбекским контентом`

---

### [x] 2.6 Написать unit-тесты для моделей

**Что сделать:**
- Создать `apps/accounts/tests/__init__.py` и `apps/accounts/tests/test_models.py`:
  - `test_player_creation` — создание игрока с nickname
  - `test_player_nickname_unique` — IntegrityError при дублировании
  - `test_player_str` — __str__ возвращает nickname
  - `test_player_default_values` — total_score=0, avatar="default"

- Создать `apps/game/tests/__init__.py` и `apps/game/tests/test_models.py`:
  - `test_level_creation` — создание уровня
  - `test_level_ordering` — уровни упорядочены по number
  - `test_eco_action_creation` — создание с impact-значениями
  - `test_game_progress_unique_together` — уникальность (player, level)
  - `test_achievement_creation` — достижение с JSONField условием
  - `test_player_achievement_unique` — уникальная связь

- Создать `apps/education/tests/__init__.py` и `apps/education/tests/test_models.py`:
  - `test_educational_content_creation`
  - `test_eco_fact_str`

- Запустить ruff: `uv run ruff check --fix .`

**Проверка:** `uv run pytest -v` — все тесты зелёные.
**Коммит:** `test: добавить unit-тесты для всех моделей`

---

## Phase 3: Backend API — Аутентификация

### [x] 3.1 Создать API аутентификации

**Что сделать:**
- Создать `apps/accounts/serializers.py`:
  ```python
  class RegisterSerializer(serializers.ModelSerializer):
      password = serializers.CharField(write_only=True, min_length=8)
      password_confirm = serializers.CharField(write_only=True)

      class Meta:
          model = Player
          fields = ["username", "nickname", "email", "password", "password_confirm"]

      def validate(self, attrs: dict) -> dict:
          if attrs["password"] != attrs.pop("password_confirm"):
              raise serializers.ValidationError({"password_confirm": "Parollar mos kelmadi"})
          return attrs

      def create(self, validated_data: dict) -> Player:
          return Player.objects.create_user(**validated_data)

  class PlayerSerializer(serializers.ModelSerializer):
      class Meta:
          model = Player
          fields = ["id", "username", "nickname", "email", "avatar", "total_score", "date_joined"]
          read_only_fields = ["id", "username", "total_score", "date_joined"]
  ```

- Создать `apps/accounts/views.py`:
  ```python
  class RegisterView(CreateAPIView):
      serializer_class = RegisterSerializer
      permission_classes = [AllowAny]

  class PlayerProfileView(RetrieveUpdateAPIView):
      serializer_class = PlayerSerializer
      permission_classes = [IsAuthenticated]

      def get_object(self) -> Player:
          return self.request.user
  ```

- Создать `apps/accounts/urls.py`:
  ```python
  urlpatterns = [
      path("register/", RegisterView.as_view()),
      path("login/", TokenObtainPairView.as_view()),
      path("token/refresh/", TokenRefreshView.as_view()),
      path("me/", PlayerProfileView.as_view()),
  ]
  ```

- Обновить `config/urls.py`:
  ```python
  urlpatterns = [
      path("admin/", admin.site.urls),
      path("api/v1/auth/", include("apps.accounts.urls")),
  ]
  ```

**Проверка:** `uv run python manage.py check` без ошибок. Проверить через curl или Postman: POST /api/v1/auth/register/, POST /api/v1/auth/login/.
**Коммит:** `feat: добавить API аутентификации (регистрация, JWT, профиль)`

---

### [x] 3.2 Написать тесты для API аутентификации

**Что сделать:**
- Создать `apps/accounts/tests/test_api.py`:
  - `test_register_success` — POST /api/v1/auth/register/ → 201, возвращает данные игрока
  - `test_register_password_mismatch` — пароли не совпадают → 400
  - `test_register_duplicate_username` → 400
  - `test_login_success` → 200, возвращает access + refresh
  - `test_login_wrong_password` → 401
  - `test_token_refresh` → 200, новый access token
  - `test_profile_get_authenticated` → 200, данные текущего игрока
  - `test_profile_update_nickname` → 200, nickname обновлён
  - `test_profile_unauthorized` → 401

- Использовать `pytest.fixture` с `@pytest.fixture def player(db)` для создания тестового игрока
- Использовать `APIClient` из DRF

**Проверка:** `uv run pytest apps/accounts/ -v` — все тесты зелёные.
**Коммит:** `test: добавить тесты API аутентификации`

---

## Phase 4: Backend API — Игровая логика

### [x] 4.1 Создать GameService

**Что сделать:**
- Создать `apps/game/services.py`:
  ```python
  from django.db import transaction
  from django.utils import timezone

  class GameService:
      """Бизнес-логика игры. Все мутации состояния проходят через этот сервис."""

      @staticmethod
      @transaction.atomic
      def start_session(player: Player, level: Level) -> tuple[GameSession, GameProgress]:
          """Начать сессию. Создаёт GameProgress если не существует."""
          session = GameSession.objects.create(player=player, level=level)
          progress, _ = GameProgress.objects.get_or_create(
              player=player,
              level=level,
              defaults={
                  "air_quality": level.ecosystem_initial.get("air", 30),
                  "water_purity": level.ecosystem_initial.get("water", 25),
                  "soil_health": level.ecosystem_initial.get("soil", 20),
                  "biodiversity": level.ecosystem_initial.get("biodiversity", 15),
              }
          )
          return session, progress

      @staticmethod
      @transaction.atomic
      def end_session(session: GameSession) -> GameProgress:
          """Завершить сессию. Обновить total_score игрока."""
          session.ended_at = timezone.now()
          session.is_active = False
          session.save(update_fields=["ended_at", "is_active"])
          progress = GameProgress.objects.get(player=session.player, level=session.level)
          # Обновить total_score игрока (сумма всех score по уровням)
          from django.db.models import Sum
          total = GameProgress.objects.filter(player=session.player).aggregate(Sum("score"))["score__sum"] or 0
          session.player.total_score = total
          session.player.save(update_fields=["total_score"])
          return progress

      @staticmethod
      @transaction.atomic
      def perform_actions(session: GameSession, actions: list[dict]) -> tuple[GameProgress, list[Achievement]]:
          """Обработать батч действий. Обновить прогресс.
          actions = [{"action_key": str, "position_x": float, "position_y": float}]
          """
          progress = GameProgress.objects.select_for_update().get(player=session.player, level=session.level)

          for action_data in actions:
              try:
                  action = EcoAction.objects.get(key=action_data["action_key"])
              except EcoAction.DoesNotExist:
                  continue

              # Применить impact на индикаторы
              new_state = GameService.calculate_ecosystem(progress, action)
              progress.air_quality = new_state["air"]
              progress.water_purity = new_state["water"]
              progress.soil_health = new_state["soil"]
              progress.biodiversity = new_state["biodiversity"]

              # Начислить очки
              progress.score += action.score_value

              # Обновить счётчик действий
              performed = progress.actions_performed
              performed[action.key] = performed.get(action.key, 0) + 1
              progress.actions_performed = performed

              # Записать лог
              delta = {"air": new_state["air"] - progress.air_quality,
                       "water": new_state["water"] - progress.water_purity}
              ActionLog.objects.create(
                  session=session, action=action,
                  position_x=action_data.get("position_x", 0),
                  position_y=action_data.get("position_y", 0),
                  result_delta=delta
              )

          # Проверить завершение уровня
          if GameService.check_level_completion(progress):
              progress.completed = True
              progress.completed_at = timezone.now()

          progress.save()

          # Проверить достижения
          new_achievements = GameService.check_achievements(session.player, progress)
          return progress, new_achievements

      @staticmethod
      def calculate_ecosystem(progress: GameProgress, action: EcoAction) -> dict:
          """Рассчитать новые значения индикаторов после действия."""
          SCALE = 10.0  # Множитель для float impact значений
          return {
              "air": min(100.0, max(0.0, progress.air_quality + action.air_impact * SCALE)),
              "water": min(100.0, max(0.0, progress.water_purity + action.water_impact * SCALE)),
              "soil": min(100.0, max(0.0, progress.soil_health + action.soil_impact * SCALE)),
              "biodiversity": min(100.0, max(0.0, progress.biodiversity + action.biodiversity_impact * SCALE)),
          }

      @staticmethod
      def check_achievements(player: Player, progress: GameProgress) -> list[Achievement]:
          """Выдать новые достижения. Возвращает список только что разблокированных."""
          already_unlocked = set(player.achievements.values_list("achievement_id", flat=True))
          all_achievements = Achievement.objects.exclude(id__in=already_unlocked)
          newly_unlocked = []

          for achievement in all_achievements:
              if GameService._check_condition(achievement, player, progress):
                  PlayerAchievement.objects.create(player=player, achievement=achievement)
                  newly_unlocked.append(achievement)

          return newly_unlocked

      @staticmethod
      def _check_condition(achievement: Achievement, player: Player, progress: GameProgress) -> bool:
          """Проверить условие достижения."""
          cv = achievement.condition_value
          ct = achievement.condition_type
          if ct == "SCORE":
              return progress.score >= cv.get("min_score", 0)
          elif ct == "ACTION_COUNT":
              key = cv.get("action_key", "")
              count = cv.get("count", 1)
              return progress.actions_performed.get(key, 0) >= count
          elif ct == "LEVEL_COMPLETE":
              return progress.completed and progress.level.number == cv.get("level_number", 1)
          elif ct == "INDICATOR":
              indicator = cv.get("indicator", "air")
              min_val = cv.get("min_value", 80)
              vals = {"air": progress.air_quality, "water": progress.water_purity,
                      "soil": progress.soil_health, "biodiversity": progress.biodiversity}
              return vals.get(indicator, 0) >= min_val
          return False

      @staticmethod
      def check_level_completion(progress: GameProgress) -> bool:
          """Уровень завершён когда все 4 индикатора >= 80."""
          return all([
              progress.air_quality >= 80,
              progress.water_purity >= 80,
              progress.soil_health >= 80,
              progress.biodiversity >= 80,
          ])
  ```

**Проверка:** `uv run python manage.py check` без ошибок.
**Коммит:** `feat: добавить GameService с бизнес-логикой игры`

---

### [x] 4.2 Создать сериализаторы и вьюхи для Game API

**Что сделать:**
- Создать `apps/game/serializers.py` с:
  - `LevelSerializer` — все поля + computed `is_unlocked` через `SerializerMethodField`
  - `EcoActionSerializer` — все поля EcoAction
  - `GameProgressSerializer` — прогресс с вложенным LevelSerializer
  - `ActionBatchSerializer` — `{"actions": [{"action_key": str, "position_x": float, "position_y": float}]}`
  - `GameSessionSerializer` — данные сессии
  - `AchievementSerializer` — с `is_unlocked` полем
  - `PlayerAchievementSerializer` — с вложенным AchievementSerializer

- Создать `apps/game/views.py`:
  - `LevelListView` — GET /api/v1/game/levels/ (AllowAny)
  - `LevelDetailView` — GET /api/v1/game/levels/{id}/
  - `EcoActionListView` — GET /api/v1/game/actions/?level={id}
  - `GameProgressListView` — GET /api/v1/game/progress/ (текущий игрок)
  - `GameProgressDetailView` — GET /api/v1/game/progress/{level_id}/
  - `SessionStartView` — POST /api/v1/game/sessions/start/
  - `SessionEndView` — POST /api/v1/game/sessions/{id}/end/
  - `ActionSubmitView` — POST /api/v1/game/sessions/{id}/actions/
  - `AchievementListView` — GET /api/v1/game/achievements/
  - `MyAchievementsView` — GET /api/v1/game/achievements/my/

- Создать `apps/game/urls.py` и подключить к `config/urls.py` через `path("api/v1/game/", ...)`

**Проверка:** `uv run python manage.py check`. Протестировать через curl: получить список уровней.
**Коммит:** `feat: добавить Game API (уровни, действия, прогресс, сессии, достижения)`

---

### [x] 4.3 Создать Education API, Leaderboard API и Django signals

**Что сделать:**
- Создать `apps/education/serializers.py`, `views.py`, `urls.py`:
  - GET /api/v1/education/articles/ — список статей (AllowAny, фильтр ?category=)
  - GET /api/v1/education/articles/{id}/ — детали
  - GET /api/v1/education/facts/random/ — случайный факт (AllowAny)

- Создать `apps/leaderboard/serializers.py`, `views.py`, `urls.py`:
  - GET /api/v1/leaderboard/ — топ 50, пагинация (AllowAny)
  - GET /api/v1/leaderboard/me/ — ранг текущего игрока (IsAuthenticated)

- Создать `apps/leaderboard/signals.py`:
  ```python
  from django.db.models.signals import post_save
  from django.dispatch import receiver
  from apps.game.models import GameProgress, PlayerAchievement
  from .models import LeaderboardEntry

  @receiver(post_save, sender=GameProgress)
  def update_leaderboard_on_progress(sender, instance: GameProgress, **kwargs) -> None:
      """Обновить лидерборд при изменении прогресса."""
      from django.db.models import Sum, Count
      player = instance.player
      stats = GameProgress.objects.filter(player=player).aggregate(
          total=Sum("score"),
          completed=Count("id", filter=models.Q(completed=True))
      )
      achievement_count = player.achievements.count()
      entry, _ = LeaderboardEntry.objects.get_or_create(player=player)
      entry.total_score = stats["total"] or 0
      entry.levels_completed = stats["completed"] or 0
      entry.achievements_count = achievement_count
      entry.save(update_fields=["total_score", "levels_completed", "achievements_count", "updated_at"])
      # Пересчитать ранги
      for rank, e in enumerate(LeaderboardEntry.objects.order_by("-total_score"), start=1):
          if e.rank != rank:
              LeaderboardEntry.objects.filter(pk=e.pk).update(rank=rank)
  ```

- Подключить signals в `apps/leaderboard/apps.py` → `ready()`
- Добавить все URLs в `config/urls.py`

**Проверка:** `uv run python manage.py check`
**Коммит:** `feat: добавить Education API, Leaderboard API, Django signals`

---

### [x] 4.4 Написать тесты для Game API и запустить полный набор

**Что сделать:**
- Создать `apps/game/tests/test_services.py`:
  - `test_start_session_creates_progress` — GameService.start_session создаёт прогресс
  - `test_perform_actions_updates_indicators` — индикаторы меняются
  - `test_ecosystem_calculation` — проверка формулы (clamp 0-100)
  - `test_achievement_unlock` — достижение выдаётся при выполнении условия
  - `test_level_completion_at_80` — уровень завершается при all >= 80

- Создать `apps/game/tests/test_api.py`:
  - `test_levels_list_unauthorized` — 200 (AllowAny)
  - `test_start_session_creates_progress` — полный flow
  - `test_action_batch_submit` — батч обрабатывается

- Создать `apps/leaderboard/tests/test_api.py`:
  - `test_leaderboard_ordered_by_score` — правильный порядок
  - `test_signal_updates_leaderboard` — сигнал срабатывает

- Запустить ruff на весь backend: `uv run ruff check --fix .`
- Запустить все тесты: `uv run pytest -v --tb=short`

**Проверка:** Все тесты зелёные, ruff без ошибок.
**Коммит:** `test: добавить тесты Game API и Leaderboard, исправить линт`

---

## Phase 5: Frontend — Роутинг, Auth, API-клиент

### [x] 5.1 Создать API-клиент и TypeScript типы

**Что сделать:**
- Создать `src/api/types.ts` — строгие TypeScript типы (без `any`):
  ```typescript
  export interface Player {
    id: number;
    username: string;
    nickname: string;
    email: string;
    avatar: string;
    total_score: number;
    date_joined: string;
  }

  export interface EcosystemState {
    air: number;
    water: number;
    soil: number;
    biodiversity: number;
  }

  export interface Level {
    id: number;
    number: number;
    name_uz: string;
    description_uz: string;
    required_score: number;
    map_config: MapConfig;
    ecosystem_initial: EcosystemState;
    is_unlocked: boolean;
  }

  export interface MapConfig {
    width: number;
    height: number;
    zones: MapZone[];
  }

  export interface MapZone {
    type: "FLORA" | "WATER" | "WASTE" | "ENERGY" | "FAUNA";
    x: number;
    y: number;
  }

  export interface EcoAction {
    id: number;
    key: string;
    name_uz: string;
    description_uz: string;
    category: "FLORA" | "WATER" | "WASTE" | "ENERGY" | "FAUNA";
    score_value: number;
    air_impact: number;
    water_impact: number;
    soil_impact: number;
    biodiversity_impact: number;
    cooldown_seconds: number;
    sprite_key: string;
  }

  export interface GameProgress {
    id: number;
    level: Level;
    score: number;
    air_quality: number;
    water_purity: number;
    soil_health: number;
    biodiversity: number;
    actions_performed: Record<string, number>;
    completed: boolean;
    completed_at: string | null;
    updated_at: string;
  }

  export interface GameSession {
    id: number;
    level: number;
    started_at: string;
    ended_at: string | null;
    is_active: boolean;
  }

  export interface Achievement {
    id: number;
    key: string;
    name_uz: string;
    description_uz: string;
    icon: string;
    condition_type: string;
    is_unlocked: boolean;
  }

  export interface LeaderboardEntry {
    rank: number;
    player_nickname: string;
    player_avatar: string;
    total_score: number;
    levels_completed: number;
    achievements_count: number;
  }

  export interface EducationalContent {
    id: number;
    title_uz: string;
    body_uz: string;
    category: string;
    image: string;
    order: number;
  }

  export interface EcoFact {
    id: number;
    text_uz: string;
    source: string;
    category: string;
  }

  export interface AuthTokens {
    access: string;
    refresh: string;
  }

  export interface RegisterData {
    username: string;
    nickname: string;
    email: string;
    password: string;
    password_confirm: string;
  }
  ```

- Создать `src/api/client.ts`:
  - Axios instance с `baseURL: import.meta.env.VITE_API_URL`
  - Request interceptor: добавляет Bearer token из localStorage
  - Response interceptor: при 401 пробует refresh, при неудаче очищает токены

- Создать `src/api/auth.ts`, `src/api/game.ts`, `src/api/education.ts`, `src/api/leaderboard.ts` — все с правильными типами возвращаемых значений

**Проверка:** `npm run build` — без TypeScript ошибок.
**Коммит:** `feat: добавить API-клиент и TypeScript типы`

---

### [x] 5.2 Создать Zustand stores и i18n

**Что сделать:**
- Создать `src/i18n/uz.json` — полный файл переводов:
  ```json
  {
    "app_name": "EcoGame",
    "tagline": "Tabiatni asrang, o'yin orqali o'rganang",
    "nav": {
      "home": "Bosh sahifa",
      "play": "O'ynash",
      "leaderboard": "Yetakchilar",
      "education": "Ta'lim",
      "profile": "Profil",
      "login": "Kirish",
      "register": "Ro'yxatdan o'tish",
      "logout": "Chiqish"
    },
    "game": {
      "air_quality": "Havo sifati",
      "water_purity": "Suv tozaligi",
      "soil_health": "Tuproq holati",
      "biodiversity": "Biologik xilma-xillik",
      "score": "Ball",
      "level": "Daraja",
      "start": "Boshlash",
      "pause": "Pauza",
      "resume": "Davom ettirish",
      "quit": "Chiqish",
      "level_complete": "Daraja tugallandi!",
      "loading": "Yuklanmoqda..."
    },
    "auth": {
      "username": "Foydalanuvchi nomi",
      "password": "Parol",
      "confirm_password": "Parolni tasdiqlang",
      "nickname": "Nik",
      "email": "Elektron pochta",
      "login_btn": "Kirish",
      "register_btn": "Ro'yxatdan o'tish",
      "no_account": "Hisobingiz yo'qmi?",
      "have_account": "Hisobingiz bormi?"
    },
    "levels": {
      "locked": "Qulflangan",
      "unlocked": "Ochiq",
      "completed": "Bajarildi",
      "required_score": "Kerakli ball"
    },
    "achievements": {
      "title": "Yutuqlar",
      "unlocked_at": "Ochilgan"
    },
    "education": {
      "title": "Ekologik ta'lim",
      "read_more": "Ko'proq o'qish",
      "fact_of_day": "Kunning ekologik fakti"
    }
  }
  ```

- Создать `src/i18n/index.ts`:
  ```typescript
  import uz from "./uz.json";

  type NestedKey<T extends object> = {
    [K in keyof T]: T[K] extends object ? `${string & K}.${string & keyof T[K]}` : string & K;
  }[keyof T];

  export function t(key: string): string {
    const keys = key.split(".");
    let result: unknown = uz;
    for (const k of keys) {
      if (typeof result === "object" && result !== null) {
        result = (result as Record<string, unknown>)[k];
      }
    }
    return typeof result === "string" ? result : key;
  }
  ```

- Создать `src/stores/authStore.ts`, `src/stores/gameStore.ts`, `src/stores/uiStore.ts`
  - authStore: player, tokens, isAuthenticated, login, logout, fetchProfile
  - gameStore: currentLevel, currentSession, progress, ecosystem, score, levels, actions, achievements
  - uiStore: isLoading, сеттеры

**Проверка:** `npm run build` без ошибок.
**Коммит:** `feat: добавить Zustand stores и i18n (узбекский)`

---

### [x] 5.3 Настроить роутинг и создать Layout, страницы

**Что сделать:**
- Создать `src/components/Layout.tsx` — с навигацией на узбекском
- Создать `src/components/ProtectedRoute.tsx` — редирект на /login
- Создать `src/components/HealthBar.tsx` — переиспользуемая полоска индикатора (с цветовой кодировкой red/yellow/green)
- Создать `src/components/LoadingScreen.tsx` — спиннер + EcoFact
- Настроить React Router в `src/App.tsx`:
  ```typescript
  // Routes:
  // / → MainMenu
  // /login → LoginPage
  // /register → RegisterPage
  // /play/:levelId → GamePage (protected)
  // /leaderboard → LeaderboardPage
  // /education → EducationPage
  // /education/:id → EducationDetailPage
  // /profile → ProfilePage (protected)
  ```
- Создать все страницы (полноценные, не плейсхолдеры):
  - `LoginPage.tsx` — форма, zod валидация, тексты на узбекском
  - `RegisterPage.tsx` — форма с полями, валидация
  - `MainMenu.tsx` — сетка уровней, статистика игрока, EcoFact
  - `LeaderboardPage.tsx` — таблица с рангами
  - `EducationPage.tsx` — список статей с фильтрами
  - `EducationDetailPage.tsx` — полная статья
  - `ProfilePage.tsx` — достижения, статистика

**Проверка:** `npm run build`. `npm run dev` → проверить все страницы, навигация работает, тексты на узбекском.
**Коммит:** `feat: добавить роутинг, Layout, все страницы приложения`

---

## Phase 6: Phaser.js — Базовая настройка

### [x] 6.1 Создать EventBus и PhaserGame компонент

**Что сделать:**
- Создать `src/game/events/EventBus.ts`:
  ```typescript
  import Phaser from "phaser";

  export type GameEventMap = {
    "score-updated": { score: number };
    "ecosystem-changed": { air: number; water: number; soil: number; biodiversity: number };
    "action-performed": { actionKey: string; positionX: number; positionY: number };
    "achievement-unlocked": { achievementKey: string; nameUz: string; icon: string };
    "level-completed": { levelNumber: number };
    "game-paused": Record<string, never>;
    "game-resumed": Record<string, never>;
  };

  export const EventBus = new Phaser.Events.EventEmitter();
  ```

- Создать `src/game/data/constants.ts`:
  ```typescript
  export const GAME_WIDTH = 800;
  export const GAME_HEIGHT = 600;
  export const TILE_SIZE = 32;
  export const INDICATOR_MAX = 100;
  export const INDICATOR_COMPLETION_THRESHOLD = 80;
  export const SYNC_INTERVAL_MS = 15_000;
  export const DECAY_RATE = { air: 0.02, water: 0.015, soil: 0.01, biodiversity: 0.025 };
  export const ECOSYSTEM_SCALE = 10.0;
  ```

- Создать `src/game/PhaserGame.tsx`:
  ```typescript
  interface PhaserGameProps {
    levelId: number;
    levelConfig: Level;
    onEcosystemChange: (state: EcosystemState) => void;
    onScoreChange: (score: number) => void;
    onActionPerformed: (actionKey: string, posX: number, posY: number) => void;
    onAchievementUnlocked: (key: string, nameUz: string) => void;
    onLevelCompleted: (levelNumber: number) => void;
  }

  export const PhaserGame = forwardRef<Phaser.Game, PhaserGameProps>(({ levelConfig, ...handlers }, ref) => {
    const gameContainerRef = useRef<HTMLDivElement>(null);
    const gameRef = useRef<Phaser.Game | null>(null);

    useEffect(() => {
      if (!gameContainerRef.current) return;

      const config: Phaser.Types.Core.GameConfig = {
        type: Phaser.AUTO,
        width: GAME_WIDTH,
        height: GAME_HEIGHT,
        parent: gameContainerRef.current,
        scene: [BootScene, PreloadScene, MainScene, HUDScene],
        physics: { default: "arcade", arcade: { debug: false } },
        scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
        audio: { disableWebAudio: false },
      };

      const game = new Phaser.Game(config);
      game.registry.set("levelConfig", levelConfig);
      gameRef.current = game;

      // Подписки на EventBus
      EventBus.on("ecosystem-changed", handlers.onEcosystemChange);
      EventBus.on("score-updated", (d: { score: number }) => handlers.onScoreChange(d.score));
      // ... остальные события

      return () => {
        EventBus.removeAllListeners();
        game.destroy(true);
        gameRef.current = null;
      };
    }, []);

    return <div ref={gameContainerRef} className="w-full h-full" />;
  });
  ```

- Создать `src/pages/GamePage.tsx`:
  - Загружает данные уровня, рендерит `<PhaserGame>`, синхронизирует с API

**Проверка:** `npm run build` без ошибок.
**Коммит:** `feat: добавить EventBus и PhaserGame компонент`

---

### [x] 6.2 Создать игровые сцены (Boot, Preload, HUD)

**Что сделать:**
- Создать `src/game/scenes/BootScene.ts`:
  - preload: загрузить логотип (минимальный ассет)
  - create: перейти к PreloadScene

- Создать `src/game/scenes/PreloadScene.ts`:
  - preload: создать прогресс-бар, загрузить все ассеты:
    ```typescript
    // Тайлсет
    this.load.image("tileset", "/assets/sprites/tileset.png");
    // Спрайты
    this.load.spritesheet("trees", "/assets/sprites/trees.png", { frameWidth: 32, frameHeight: 64 });
    this.load.spritesheet("player", "/assets/sprites/player.png", { frameWidth: 32, frameHeight: 48 });
    // UI
    this.load.image("ui-icons", "/assets/ui/icons.png");
    // Звуки
    this.load.audio("plant", "/assets/audio/plant.mp3");
    this.load.audio("ambient", "/assets/audio/ambient.mp3");
    ```
  - create: показать случайный EcoFact (из registry), через 2 сек → MainScene

- Создать `src/game/scenes/HUDScene.ts`:
  - Параллельная сцена с индикаторами
  - Четыре HealthBar-подобных полоски (рисуются через Phaser Graphics)
  - Счёт в правом верхнем углу
  - Кнопка паузы
  - Метод `showAchievementToast(nameUz, icon)` — анимированное уведомление
  - Слушает EventBus "ecosystem-changed" и "score-updated"

- Создать `src/game/scenes/MainScene.ts` (скелет):
  - create(): инициализировать TileMap, создать зоны
  - update(): вызывать ecosystem tick

**Проверка:** `npm run build`. `npm run dev` → /play/1 → загрузочный экран с прогресс-баром, затем пустая сцена с HUD.
**Коммит:** `feat: добавить игровые сцены Boot, Preload, HUD`

---

### [x] 6.3 Создать игровые ассеты (спрайты, звуки)

**Что сделать:**
- Создать директории: `public/assets/sprites/`, `public/assets/audio/`, `public/assets/ui/`
- Создать минимальные PNG ассеты (пиксель-арт или цветные прямоугольники):
  - `tileset.png` (320x320, 10x10 тайлов 32x32) — трава, земля, вода, песок, камень, цветок, дерево-пень, мусор, панель, забор
  - `trees.png` (96x64, 3 кадра: саженец, маленькое дерево, большое дерево)
  - `water.png` (64x32, 2 кадра: грязная, чистая вода)
  - `player.png` (32x48, спрайт персонажа)
  - `animals.png` (32x32 x4 кадра: птица, рыба, олень, бабочка)
  - `icons.png` (16x16 x4: иконки воздух, вода, почва, биоразнообразие)
  - `particles.png` (8x8, для эффектов)
  - Если создание PNG затруднено — скачать свободные ассеты с OpenGameArt.org и указать лицензию
- Создать `public/assets/audio/`:
  - `ambient.mp3` — фоновые звуки природы (30 сек, loop)
  - `plant.mp3` — звук посадки
  - `water_clean.mp3` — звук воды
  - `achievement.mp3` — звук достижения
  - `click.mp3` — звук клика
  - Можно использовать свободные звуки с freesound.org или сгенерировать через Tone.js

**Проверка:** Все файлы существуют в `public/assets/`, PreloadScene загружает без 404 ошибок в консоли.
**Коммит:** `feat: добавить игровые ассеты (спрайты, звуки)`

---

## Phase 7: Phaser.js — Геймплей

### [x] 7.1 Создать игровые объекты

**Что сделать:**
- Создать `src/game/objects/InteractiveZone.ts`:
  - Extends Phaser.GameObjects.Zone
  - `zoneType: "FLORA" | "WATER" | "WASTE" | "ENERGY" | "FAUNA"`
  - Пульсирующая подсветка при hover
  - Метод `showActionMenu(actions: EcoAction[])` — показать меню действий
  - Метод `hideActionMenu()`

- Создать `src/game/objects/Tree.ts`:
  - Extends Phaser.GameObjects.Sprite
  - Состояния через enum: EMPTY, SAPLING, GROWING, MATURE
  - Метод `plant()` — анимация роста (tween scale)

- Создать `src/game/objects/WaterSource.ts`:
  - Tint для визуализации (0x8B4513 → 0x4169E1)
  - Метод `clean()` — tween изменения tint

- Создать `src/game/objects/WasteBin.ts`, `SolarPanel.ts`, `Animal.ts` — аналогично

**Проверка:** `npm run build` без TypeScript ошибок.
**Коммит:** `feat: добавить игровые объекты (Tree, WaterSource, WasteBin, SolarPanel, Animal)`

---

### [x] 7.2 Создать системы (EcosystemManager, ActionSystem, ScoreSystem)

**Что сделать:**
- Создать `src/game/systems/EcosystemManager.ts`:
  ```typescript
  export class EcosystemManager {
    private state: EcosystemState;
    private decayTimer = 0;

    constructor(initialState: EcosystemState) {
      this.state = { ...initialState };
    }

    tick(delta: number): void {
      this.decayTimer += delta;
      if (this.decayTimer < 1000) return; // Каждую секунду
      this.decayTimer = 0;

      // Деградация
      this.state.air = Math.max(0, this.state.air - DECAY_RATE.air);
      this.state.water = Math.max(0, this.state.water - DECAY_RATE.water);
      this.state.soil = Math.max(0, this.state.soil - DECAY_RATE.soil);
      this.state.biodiversity = Math.max(0, this.state.biodiversity - DECAY_RATE.biodiversity);

      // Compound effect: высокое биоразнообразие улучшает всё
      if (this.state.biodiversity > 50) {
        const bonus = (this.state.biodiversity - 50) * 0.001;
        this.state.air = Math.min(100, this.state.air + bonus);
        this.state.water = Math.min(100, this.state.water + bonus);
        this.state.soil = Math.min(100, this.state.soil + bonus);
      }

      EventBus.emit("ecosystem-changed", { ...this.state });
    }

    applyAction(action: Pick<EcoAction, "air_impact" | "water_impact" | "soil_impact" | "biodiversity_impact">): void {
      this.state.air = Math.min(100, Math.max(0, this.state.air + action.air_impact * ECOSYSTEM_SCALE));
      this.state.water = Math.min(100, Math.max(0, this.state.water + action.water_impact * ECOSYSTEM_SCALE));
      this.state.soil = Math.min(100, Math.max(0, this.state.soil + action.soil_impact * ECOSYSTEM_SCALE));
      this.state.biodiversity = Math.min(100, Math.max(0, this.state.biodiversity + action.biodiversity_impact * ECOSYSTEM_SCALE));
      EventBus.emit("ecosystem-changed", { ...this.state });
    }

    getState(): EcosystemState { return { ...this.state }; }
    isLevelComplete(): boolean {
      return this.state.air >= 80 && this.state.water >= 80 && this.state.soil >= 80 && this.state.biodiversity >= 80;
    }
  }
  ```

- Создать `src/game/systems/ActionSystem.ts`:
  - Управляет кулдаунами (Map<actionKey, lastUsedTime>)
  - Метод `performAction(zone, action, scene)` — проверяет кулдаун, запускает анимацию объекта, вызывает ecosystemManager.applyAction(), emit "action-performed"
  - Метод `canPerform(actionKey)` — проверяет кулдаун

- Создать `src/game/systems/ScoreSystem.ts`:
  - Накапливает score
  - Метод `addPoints(points, combo?)` — добавить очки с опциональным комбо-множителем
  - Emit "score-updated"

**Проверка:** `npm run build` без ошибок.
**Коммит:** `feat: добавить системы EcosystemManager, ActionSystem, ScoreSystem`

---

### [x] 7.3 Реализовать полноценный MainScene

**Что сделать:**
- Полностью реализовать `src/game/scenes/MainScene.ts`:
  - `create()`:
    1. Получить levelConfig из `this.game.registry.get("levelConfig")`
    2. Создать фоновый слой тайлов (программно, без Tiled):
       ```typescript
       // Создать TileMap программно
       const map = this.make.tilemap({ width: config.map_config.width, height: config.map_config.height, tileWidth: TILE_SIZE, tileHeight: TILE_SIZE });
       const tileset = map.addTilesetImage("tileset");
       const layer = map.createBlankLayer("ground", tileset);
       // Заполнить базовыми тайлами (трава)
       layer.fill(0); // tile index 0 = grass
       ```
    3. Создать InteractiveZone для каждой зоны из config.map_config.zones
    4. Создать игровые объекты в зонах (Tree в FLORA зонах, WaterSource в WATER, и т.д.)
    5. Инициализировать EcosystemManager, ActionSystem, ScoreSystem
    6. Настроить camera bounds (если карта больше экрана — прокрутка)
    7. Запустить HUDScene: `this.scene.launch("HUDScene")`
    8. Настроить input: `this.input.on("pointerdown", ...)`

  - `update(time, delta)`:
    1. `this.ecosystemManager.tick(delta)`
    2. Обновить визуальное состояние:
       - Фоновый цвет (небо) на основе air_quality
       - Tint воды на основе water_purity
       - Видимость животных на основе biodiversity
    3. Проверить level completion: если `ecosystemManager.isLevelComplete()` → `EventBus.emit("level-completed", ...)`

  - Обработка кликов на InteractiveZone:
    - Показать выпадающее меню с доступными действиями (Phaser Graphics + Text)
    - При выборе действия: `actionSystem.performAction(zone, action, this)`

- Реализовать простое меню действий (ActionMenu) как часть MainScene — список кнопок при клике на зону

**Проверка:** `npm run dev` → /play/1 → карта рендерится, клик на зону показывает меню действий, выполнение действия меняет индикаторы в HUD.
**Коммит:** `feat: реализовать полноценный MainScene с геймплеем`

---

### [x] 7.4 Подключить Phaser к API синхронизации

**Что сделать:**
- Обновить `src/pages/GamePage.tsx`:
  - При маунте: вызвать `gameStore.startGame(levelId)` → POST /sessions/start/
  - Буфер действий: `const actionsBuffer = useRef<ActionData[]>([])`
  - Слушать EventBus "action-performed" → push в буфер
  - `useEffect` с `setInterval(SYNC_INTERVAL_MS)`:
    - Если буфер не пуст: POST /sessions/{id}/actions/ с буфером, очистить буфер
  - Слушать "level-completed" → POST /sessions/{id}/end/ → показать поздравление → navigate("/")
  - Cleanup: при анмаунте → отправить остаток буфера → POST /sessions/{id}/end/

- Создать `src/hooks/useGameSync.ts`:
  ```typescript
  export function useGameSync(sessionId: number | null) {
    const actionsBufferRef = useRef<ActionData[]>([]);

    const addAction = useCallback((action: ActionData) => {
      actionsBufferRef.current.push(action);
    }, []);

    const flush = useCallback(async () => {
      if (!sessionId || actionsBufferRef.current.length === 0) return;
      const actions = [...actionsBufferRef.current];
      actionsBufferRef.current = [];
      await submitActions(sessionId, actions);
    }, [sessionId]);

    useEffect(() => {
      const interval = setInterval(flush, SYNC_INTERVAL_MS);
      return () => { clearInterval(interval); flush(); };
    }, [flush]);

    return { addAction };
  }
  ```

**Проверка:** Сыграть уровень → проверить в Django Admin что ActionLog записи появляются, GameProgress обновляется.
**Коммит:** `feat: подключить Phaser к API синхронизации`

---

## Phase 8: Достижения, полировка, интеграция

### [x] 8.1 Реализовать систему достижений и уведомлений

**Что сделать:**
- В `src/game/systems/ActionSystem.ts` добавить проверку достижений:
  - После каждого действия: `checkAchievements(actionsPerformed, score, ecosystemState)`
  - Сравнить с условиями из `gameStore.achievements`
  - Если unlock → `EventBus.emit("achievement-unlocked", ...)`
  - `EventBus.emit` не `emit` дважды — хранить Set уже выданных

- В `src/game/scenes/HUDScene.ts` реализовать `showAchievementToast()`:
  - Phaser Graphics + Text с фоном
  - Tween: slide-in снизу → пауза 3 сек → fade-out
  - Звук `achievement.mp3`

- В `src/pages/GamePage.tsx`:
  - Слушать "achievement-unlocked" → `toast.success(nameUz)` через react-hot-toast
  - Обновить `gameStore.achievements`

**Проверка:** Посадить 1 дерево → toast "Birinchi daraxt" появляется в HUD и в React UI.
**Коммит:** `feat: реализовать систему достижений и уведомлений`

---

### [x] 8.2 Создать карты для всех 4 уровней и добавить звуки

**Что сделать:**
- Обновить MainScene для поддержки разных размеров карт и наборов зон (из levelConfig.map_config)
- Создать генератор карт `src/game/data/mapGenerator.ts`:
  - Функция `generateMap(config: MapConfig)` — возвращает расположение тайлов и объектов
  - Level 1 (Kichik hovli): маленький двор с домом, садом, арыком
  - Level 2 (Mahalla): несколько домов, парк, канал
  - Level 3 (Shahar): городские блоки, река, завод
  - Level 4 (Viloyat): разнообразный ландшафт, символическое "Оральское озеро"

- Добавить звуки в MainScene:
  ```typescript
  this.sound.add("ambient", { loop: true, volume: 0.3 }).play();
  ```
- Добавить звуки в объекты при выполнении действий

- Кнопка mute в HUDScene — переключает `this.sound.mute`

**Проверка:** Все 4 уровня запускаются, карты различаются визуально, звук играет.
**Коммит:** `feat: создать карты для 4 уровней, добавить звуки`

---

### [x] 8.3 Полировка UI, responsive дизайн, финальный E2E тест

**Что сделать:**
- Обновить CSS/Tailwind стили:
  - Природная цветовая палитра (emerald, sky, amber, green)
  - Анимации переходов (CSS transitions)
  - Красивые карточки уровней
  - Стилизация форм

- Responsive дизайн:
  - Mobile (375px): вертикальный layout, touch controls
  - Tablet (768px): адаптивная сетка
  - Desktop (1280px): полный layout

- E2E тест (выполнить вручную, задокументировать):
  1. Открыть / → MainMenu
  2. Нажать "Ro'yxatdan o'tish" → RegisterPage
  3. Зарегистрироваться → автологин
  4. Выбрать Level 1 → /play/1
  5. Подождать загрузку → MainScene
  6. Кликнуть на FLORA зону → меню действий
  7. Выбрать "Daraxt ekish" → анимация, индикаторы растут, счёт +20
  8. Получить достижение "Birinchi daraxt" → toast
  9. Сыграть до завершения уровня (все >= 80) → поздравление
  10. Вернуться в MainMenu → Level 2 разблокирован
  11. Перейти /leaderboard → свой ник в таблице
  12. Перейти /education → прочитать статью
  13. Перейти /profile → достижения видны

**Проверка:** Весь E2E сценарий работает без ошибок.
**Коммит:** `feat: полировка UI, responsive дизайн, E2E проверка`

---

## Phase 9: Docker и деплой на ecogame.fullfocus.dev

### [x] 9.1 Создать production Docker-конфигурацию

**Что сделать:**
- Обновить `backend/Dockerfile` для production (с collectstatic, gunicorn)
- Создать `frontend/Dockerfile` (multi-stage: build + nginx):
  ```dockerfile
  FROM node:20-alpine AS builder
  WORKDIR /app
  COPY package.json package-lock.json ./
  RUN npm ci
  COPY . .
  ARG VITE_API_URL
  ENV VITE_API_URL=$VITE_API_URL
  RUN npm run build

  FROM nginx:alpine
  COPY --from=builder /app/dist /usr/share/nginx/html
  COPY nginx.conf /etc/nginx/conf.d/default.conf
  ```
- Создать `frontend/nginx.conf` (SPA конфиг):
  ```nginx
  server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;
    location / { try_files $uri $uri/ /index.html; }
  }
  ```
- Создать `nginx/Dockerfile` и `nginx/nginx.conf` (reverse proxy):
  - / → frontend:80
  - /api/ → backend:8000
  - /admin/ → backend:8000
  - /static/ → файлы
- Создать production `docker-compose.yml` с сервисами: postgres, backend, frontend, nginx
- Создать `backend/entrypoint.sh`:
  ```bash
  #!/bin/bash
  uv run python manage.py migrate
  uv run python manage.py collectstatic --noinput
  exec uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
  ```

**Проверка:** `docker compose up --build` — все 4 сервиса работают, http://localhost — сайт доступен.
**Коммит:** `chore: добавить production Docker конфигурацию`

---

### [x] 9.2 Настроить GitHub репозиторий и задеплоить через Coolify

**Что сделать:**
- Создать репозиторий на GitHub:
  ```bash
  gh repo create ecogame-diploma --private --source=. --push
  # или через GitHub web UI, затем git remote add origin ... && git push -u origin main
  ```
- Убедиться что .env НЕ в репозитории (проверить .gitignore)
- Войти в Coolify: https://coolify.fullfocus.dev
- Создать новый проект "EcoGame"
- Добавить Resource → Docker Compose → выбрать GitHub репозиторий
- Настроить Environment Variables в Coolify (НЕ хранить в файлах!):
  - DJANGO_SECRET_KEY (сгенерировать: `python -c "import secrets; print(secrets.token_urlsafe(50))"`)
  - DJANGO_DEBUG=False
  - DJANGO_ALLOWED_HOSTS=ecogame.fullfocus.dev
  - DATABASE_URL=postgres://ecogame:STRONG_PASSWORD@postgres:5432/ecogame
  - POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
  - CORS_ALLOWED_ORIGINS=https://ecogame.fullfocus.dev
  - VITE_API_URL=https://ecogame.fullfocus.dev/api/v1
- Настроить домен: ecogame.fullfocus.dev → SSL через Let's Encrypt
- Нажать Deploy
- После деплоя загрузить данные:
  ```bash
  ssh -p 2222 deploy@89.167.60.96 "cd ecogame && docker compose exec backend uv run python manage.py loaddata fixtures/levels.json fixtures/eco_actions.json fixtures/achievements.json fixtures/educational_content.json fixtures/eco_facts.json"
  ```

**Проверка:** Открыть https://ecogame.fullfocus.dev — сайт работает по HTTPS, игра загружается, API отвечает.
**Коммит:** `chore: настроить деплой на ecogame.fullfocus.dev через Coolify`

---

## Phase 10: Документация — ВКР и презентация

### [x] 10.1 Написать Главу 1 ВКР: Аналитическая часть

**Что сделать:**
- Создать `docs/vkr/chapter1_analysis.md` (или .docx), структура:

  **1.1 Анализ экологической ситуации в Узбекистане** (~5 стр.)
  - Статистика загрязнения воздуха: ссылка на IQAir, данные по Ташкенту
  - Проблема Аральского моря: история, текущее состояние (осталось 10% воды), последствия
  - Проблема твёрдых отходов: статистика ТБО в Узбекистане
  - Биоразнообразие: Красная книга Узбекистана — сколько видов под угрозой
  - Государственные программы: "Yashil makon", стратегия развития 2022-2026

  **1.2 Геймификация в экологическом образовании** (~5 стр.)
  - Определение и принципы геймификации
  - Теория потока (Mihaly Csikszentmihalyi) — почему игры увлекают
  - Обзор аналогов (таблица: Eco, Recycle Rush, Toca Nature, SimEarth, EcoSim)
  - Эффективность: исследования о влиянии игр на экологическое поведение
  - Преимущество узбекского языка для целевой аудитории

  **1.3 Обзор технологий** (~5 стр.)
  - Backend: Django vs FastAPI vs Node.js (таблица сравнения) → выбор Django (экосистема, ORM, безопасность)
  - Frontend: React vs Vue vs Angular → выбор React (размер сообщества, Phaser интеграция)
  - Game Engine: Phaser.js vs PixiJS vs Three.js → выбор Phaser.js (2D специализация, тайлмапы)
  - Docker и Coolify для деплоя

  **1.4 Выводы по главе 1** (~1 стр.)

- Оформление (ГОСТ Р 7.0.5-2008): Times New Roman 14pt, 1.5 интервал, отступ первой строки 1.25 см, поля: лево 2.5, право 1, верх 2, низ 2 см
- Минимум 15 источников в этой главе

**Проверка:** Файл создан, минимум 15 страниц текста, 15+ ссылок на источники.
**Коммит:** `docs: написать Главу 1 ВКР — аналитическая часть`

---

### [ ] 10.2 Написать Главу 2 ВКР: Проектная часть

**Что сделать:**
- Создать `docs/vkr/chapter2_design.md`:

  **2.1 Архитектура приложения** (~4 стр.)
  - Диаграмма компонентов (Mermaid или Excalidraw): Client → Nginx → Backend API → PostgreSQL; Client → Phaser Game Engine
  - Клиент-серверная архитектура с описанием
  - Диаграмма развёртывания: Docker containers на сервере 89.167.60.96, домен ecogame.fullfocus.dev

  **2.2 Проектирование базы данных** (~4 стр.)
  - ER-диаграмма всех моделей (с атрибутами и связями)
  - Описание каждой таблицы (назначение, ключевые поля)
  - Обоснование использования JSONField для map_config и condition_value

  **2.3 REST API** (~3 стр.)
  - Таблица всех эндпоинтов (метод, путь, auth, описание)
  - Пример запроса и ответа для POST /sessions/{id}/actions/
  - JWT аутентификация: flow диаграмма

  **2.4 Игровая механика** (~5 стр.)
  - Концепция экосимулятора: 4 индикатора, деградация, compound effects
  - Система уровней: описание 4 уровней с требованиями
  - Таблица действий: ключ → влияние на индикаторы → очки
  - Система достижений: таблица условий
  - State Machine диаграмма игры
  - Use Case диаграмма

  **2.5 Пользовательский интерфейс** (~3 стр.)
  - Wireframes/макеты: MainMenu, GamePage, Leaderboard, Education, Profile
  - Мобильная адаптация

  **2.6 Выводы** (~1 стр.)

- Создать диаграммы в Mermaid и вставить в документ как код (рендерится при просмотре на GitHub)

**Проверка:** Файл создан, все диаграммы присутствуют, 15-20 страниц.
**Коммит:** `docs: написать Главу 2 ВКР — проектная часть`

---

### [ ] 10.3 Написать Главу 3 ВКР: Реализация

**Что сделать:**
- Создать `docs/vkr/chapter3_implementation.md`:

  **3.1 Среда разработки** (~2 стр.)
  - Инструменты с версиями
  - Структура монорепозитория (дерево файлов)

  **3.2 Серверная часть** (~5 стр.)
  - Модели: код Player, GameProgress, GameService.perform_actions
  - Админ-панель Unfold (скриншоты)
  - Django signals для лидерборда

  **3.3 Клиентская часть** (~5 стр.)
  - Zustand store архитектура
  - EventBus паттерн: схема + код PhaserGame.tsx
  - Сцены: Boot → Preload → Main → HUD (скриншоты)
  - EcosystemManager: формулы + код tick()

  **3.4 Локализация** (~2 стр.)
  - i18n файл uz.json (фрагмент)
  - Образовательный контент на узбекском (примеры фактов и статей)

  **3.5 Развёртывание** (~3 стр.)
  - Docker Compose схема
  - Nginx конфигурация
  - Coolify deployment скриншоты
  - SSL сертификат

  **3.6 Выводы** (~1 стр.)

- Сделать скриншоты (не менее 10):
  - Unfold Admin с данными
  - MainMenu страница
  - Игровой процесс (карта + HUD)
  - После выполнения действия (изменение индикаторов)
  - Toast достижения
  - Leaderboard
  - Education статья
  - Profile страница
  - Coolify Dashboard

**Проверка:** Файл создан, 15-20 страниц, 10+ скриншотов вставлены.
**Коммит:** `docs: написать Главу 3 ВКР — реализация`

---

### [ ] 10.4 Написать Главу 4, Введение, Заключение, Список литературы

**Что сделать:**
- Создать `docs/vkr/chapter4_testing.md`:
  - 4.1 Модульное тестирование: вывод `pytest -v --tb=short`, coverage report (цель 80%+)
  - 4.2 Интеграционное: описание E2E сценария из Phase 8.3
  - 4.3 Пользовательское: описание метода (анкета для 5-10 студентов группы)
  - 4.4 Результаты: таблица метрик (время сессии, уровней пройдено, средняя оценка)
  - 4.5 Выводы

- Создать `docs/vkr/introduction.md`:
  - Актуальность (проблемы экологии + польза геймификации)
  - Цель: "Разработать веб-приложение 'EcoGame' — экологическую игру-симулятор на узбекском языке"
  - Задачи (5-6 пунктов):
    1. Анализ экологической ситуации и аналогов
    2. Проектирование архитектуры и базы данных
    3. Разработка серверной части (Django REST API)
    4. Разработка клиентской части (React + Phaser.js)
    5. Создание образовательного контента на узбекском
    6. Тестирование и развёртывание
  - Объект, предмет, методы, практическая значимость

- Создать `docs/vkr/conclusion.md`:
  - Перечисление достигнутых результатов по задачам
  - Новизна: первая экологическая игра-симулятор на узбекском языке
  - Перспективы: мобильное приложение, мультиплеер, новые уровни (Aralsiz dengiz), AR-режим

- Создать `docs/vkr/bibliography.md` — минимум 30 источников:
  - 10+ книг (Django, React, Phaser.js, экология, геймификация, образование)
  - 10+ статей (научные журналы по экологическому образованию через игры)
  - 5+ интернет-ресурсов (документация, IQAir, UNEP данные)
  - 5+ нормативных документов (экологическое законодательство Узбекистана)
  - ГОСТ Р 7.0.5-2008 оформление

- Создать `docs/vkr/appendices/`:
  - appendix_a_code.md — листинги ключевых файлов
  - appendix_b_screenshots.md — скриншоты всех экранов
  - appendix_c_er_diagram.md — полноразмерная ER-диаграмма

**Проверка:** Все разделы ВКР созданы, общий объём оценочно 60-80 страниц, 30+ источников.
**Коммит:** `docs: написать Главу 4, Введение, Заключение, Список литературы`

---

### [ ] 10.5 Создать презентацию для защиты

**Что сделать:**
- Создать `docs/presentation/slides.md` (структура слайдов):

  **Слайд 1: Титульный**
  - Название: "Разработка экологической игры по охране окружающей среды (на узбекском языке)"
  - Автор: Рузибаев Жахонгир Дилмуратович, 036-21 SMMr
  - Руководители: Узакова М.А., Абидова Ш.Б.
  - Год: 2025

  **Слайд 2: Актуальность**
  - Проблемы экологии Узбекистана (3 пункта с цифрами)
  - QR-код на сайт игры

  **Слайд 3: Цель и задачи**
  - Цель (1 предложение)
  - 6 задач (список)

  **Слайд 4: Обзор аналогов**
  - Таблица сравнения (4 игры vs EcoGame)

  **Слайд 5: Архитектура**
  - Диаграмма компонентов

  **Слайд 6: Стек технологий**
  - Логотипы: Django + DRF + PostgreSQL / React + Phaser.js + Zustand / Docker + Coolify

  **Слайд 7: База данных**
  - ER-диаграмма (упрощённая)

  **Слайд 8: Игровая механика**
  - Схема: 4 индикатора → действия → изменения → достижения

  **Слайд 9: Демо — MainMenu**
  - Скриншот MainMenu

  **Слайд 10: Демо — Геймплей**
  - Скриншот игры (карта + HUD до и после действий)

  **Слайд 11: Демо — Дополнительные страницы**
  - Скриншоты: Leaderboard, Education, Profile

  **Слайд 12: Развёртывание**
  - Схема Docker + Coolify
  - URL: ecogame.fullfocus.dev с QR-кодом

  **Слайд 13: Результаты тестирования**
  - pytest coverage: X%
  - Таблица E2E сценариев

  **Слайд 14: Заключение и перспективы**
  - 3 достигнутых результата
  - 3 перспективы развития

  **Слайд 15: Спасибо за внимание**
  - URL игры + QR-код
  - Контакты

- Если возможно — конвертировать в PPTX или Google Slides

**Проверка:** Структура презентации создана, 15 слайдов, все скриншоты из работающего приложения.
**Коммит:** `docs: создать презентацию для защиты`

---

# ALL PHASES COMPLETE
