# Глава 3. Реализация системы EcoGame

## 3.1. Настройка среды разработки и структура проекта

### 3.1.1. Инструменты разработки

Разработка велась в следующем окружении:
- **ОС**: macOS Sequoia 15.5 (совместимо с Linux Ubuntu 22.04+)
- **Python**: 3.12.3 (управление пакетами через `uv` — быстрая альтернатива pip)
- **Node.js**: 20.18 LTS
- **Docker Desktop**: 25.0+
- **Редактор**: VS Code + Claude Code (CLI)
- **Git**: 2.45+

**Выбор `uv` вместо `pip`**: менеджер пакетов Astral uv обеспечивает в 10–100× более быструю установку зависимостей за счёт параллельного скачивания и Rust-реализации. Команда `uv sync --frozen` (детерминированная установка из `uv.lock`) критична для воспроизводимых Docker-сборок.

### 3.1.2. Структура монорепозитория

```
/Diploma/
├── backend/                # Django REST API
│   ├── apps/
│   │   ├── accounts/       # Модель Player, JWT auth
│   │   ├── education/      # Образовательный контент
│   │   ├── game/           # Уровни, действия, прогресс
│   │   └── leaderboard/    # Лидерборд + signals
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py     # Общие настройки
│   │   │   ├── dev.py      # SQLite, DEBUG=True
│   │   │   └── prod.py     # PostgreSQL, DEBUG=False
│   │   └── urls.py
│   ├── fixtures/           # JSON данные на узбекском
│   ├── Dockerfile          # Multi-stage prod образ
│   └── pyproject.toml      # uv зависимости
│
├── frontend/               # React 19 + Phaser.js
│   ├── src/
│   │   ├── api/            # HTTP-клиент + типы
│   │   ├── game/           # Phaser scenes + systems
│   │   ├── hooks/          # useGameSync, useAuth
│   │   ├── i18n/           # Переводы (uz.json)
│   │   ├── pages/          # Страницы приложения
│   │   └── stores/         # Zustand stores
│   ├── public/assets/      # Спрайты, аудио
│   ├── Dockerfile          # node → nginx multi-stage
│   └── nginx.conf          # SPA fallback
│
├── nginx/                  # Reverse proxy
│   ├── Dockerfile
│   └── nginx.conf
│
├── docs/vkr/               # ВКР документация
├── docker-compose.yml      # Production стек
├── deploy.sh               # Скрипт деплоя на сервере
└── .env.example            # Шаблон переменных окружения
```

### 3.1.3. Настройка линтеров и форматтеров

**Backend (ruff)**:
```toml
# backend/pyproject.toml
[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.dev"
python_files = "test_*.py"
```

**Frontend (ESLint + Prettier)**:
```json
// frontend/.eslintrc.json
{
  "extends": ["react-app", "@typescript-eslint/recommended"],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "no-console": "warn"
  }
}
```

---

## 3.2. Реализация серверной части (Backend)

### 3.2.1. Split Settings — разделение конфигураций

Вместо единого `settings.py` использована архитектура split settings с тремя уровнями:

```python
# backend/config/settings/base.py (фрагмент)
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()

INSTALLED_APPS = [
    "unfold",                           # Должно быть ПЕРЕД django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "rest_framework",
    "corsheaders",
    "apps.accounts",
    "apps.game",
    "apps.education",
    "apps.leaderboard",
]

AUTH_USER_MODEL = "accounts.Player"    # Кастомная модель пользователя

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}
```

```python
# backend/config/settings/prod.py (фрагмент)
from .base import *

DEBUG = False
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

DATABASES = {
    "default": env.db("DATABASE_URL")    # postgres://user:pass@host:5432/db
}

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
```

**Архитектурное решение**: `BASE_DIR` указывает на три уровня выше файла `base.py` (`parent.parent.parent`), что корректно для структуры `config/settings/base.py`.

### 3.2.2. Кастомная модель пользователя Player

```python
# backend/apps/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class Player(AbstractUser):
    """Расширенная модель игрока с игровой статистикой."""

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

**Критическое решение**: `AUTH_USER_MODEL` должна быть объявлена **до первой миграции**. После создания хотя бы одной миграции изменить базовую модель пользователя крайне сложно. В данном проекте `AUTH_USER_MODEL = "accounts.Player"` задана в `base.py` до инициализации БД.

### 3.2.3. Модели игровой логики

```python
# backend/apps/game/models.py (фрагмент — модель GameProgress)
class GameProgress(models.Model):
    """Агрегированный прогресс игрока по уровню."""

    player = models.ForeignKey(
        "accounts.Player", on_delete=models.CASCADE, related_name="progress"
    )
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="player_progress")
    score = models.PositiveIntegerField(default=0)
    air_quality = models.FloatField(default=0)
    water_purity = models.FloatField(default=0)
    soil_health = models.FloatField(default=0)
    biodiversity = models.FloatField(default=0)
    actions_performed = models.JSONField(default=dict)   # {"plant_tree": 5, "clean_water": 2}
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Прогресс игрока"
        unique_together = ("player", "level")   # один прогресс на уровень
        ordering = ["level__number"]
```

`JSONField` для `actions_performed` позволяет хранить произвольный словарь счётчиков без изменения схемы БД — ключ является строковым идентификатором действия, значение — накопленным количеством.

### 3.2.4. GameService — центральная бизнес-логика

GameService реализует паттерн Service Layer — все бизнес-операции сосредоточены в одном месте, views выступают тонким слоем маршрутизации:

```python
# backend/apps/game/services.py (фрагмент — perform_actions)
LEVEL_COMPLETION_THRESHOLD = 80.0
ACTION_IMPACT_MULTIPLIER = 10.0


class GameService:
    """Бизнес-логика игры. Все мутации проходят через этот класс."""

    @staticmethod
    @transaction.atomic
    def perform_actions(
        session: "GameSession", actions: list[dict]
    ) -> "GameProgress":
        """Обработать батч экологических действий."""
        progress, _ = GameProgress.objects.get_or_create(
            player=session.player,
            level=session.level,
            defaults={"air_quality": session.level.ecosystem_initial.get("air", 30)},
        )

        for action_data in actions:
            try:
                action = EcoAction.objects.get(key=action_data["action_key"])
            except EcoAction.DoesNotExist:
                continue

            # Рассчитать новое состояние экосистемы
            ecosystem = GameService.calculate_ecosystem(progress, action)
            progress.air_quality = ecosystem["air"]
            progress.water_purity = ecosystem["water"]
            progress.soil_health = ecosystem["soil"]
            progress.biodiversity = ecosystem["biodiversity"]

            # Начислить очки
            progress.score += action.score_value
            performed = progress.actions_performed
            performed[action.key] = performed.get(action.key, 0) + 1
            progress.actions_performed = performed

            # Записать в лог
            ActionLog.objects.create(
                session=session,
                action=action,
                position_x=action_data.get("position_x", 0),
                position_y=action_data.get("position_y", 0),
                result_delta=ecosystem,
            )

        # Проверить завершение уровня
        if GameService.check_level_completion(progress):
            progress.completed = True
            progress.completed_at = timezone.now()

        progress.save()

        # Обновить total_score игрока
        player = session.player
        player.total_score = GameProgress.objects.filter(
            player=player
        ).aggregate(total=models.Sum("score"))["total"] or 0
        player.save(update_fields=["total_score"])

        # Проверить достижения
        GameService.check_achievements(player, progress)

        return progress
```

```python
    @staticmethod
    def calculate_ecosystem(progress: "GameProgress", action: "EcoAction") -> dict:
        """Рассчитать новые значения индикаторов после действия."""
        air = progress.air_quality + action.air_impact * ACTION_IMPACT_MULTIPLIER
        water = progress.water_purity + action.water_impact * ACTION_IMPACT_MULTIPLIER
        soil = progress.soil_health + action.soil_impact * ACTION_IMPACT_MULTIPLIER
        biodiversity = progress.biodiversity + action.biodiversity_impact * ACTION_IMPACT_MULTIPLIER

        # Compound-эффект: высокое биоразнообразие улучшает другие
        if biodiversity > 50:
            bonus = (biodiversity - 50) / 10 * 0.005
            air += bonus
            water += bonus
            soil += bonus * 1.5

        return {
            "air": max(0.0, min(100.0, air)),
            "water": max(0.0, min(100.0, water)),
            "soil": max(0.0, min(100.0, soil)),
            "biodiversity": max(0.0, min(100.0, biodiversity)),
        }
```

### 3.2.5. Сигналы для лидерборда

Django signals обеспечивают автоматическую синхронизацию `LeaderboardEntry` без явных вызовов из сервисного слоя:

```python
# backend/apps/leaderboard/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.game.models import GameProgress, PlayerAchievement
from .models import LeaderboardEntry


@receiver(post_save, sender=GameProgress)
def update_leaderboard_on_progress(sender, instance: GameProgress, **kwargs) -> None:
    """Обновить лидерборд при изменении прогресса."""
    player = instance.player
    entry, _ = LeaderboardEntry.objects.get_or_create(player=player)

    from apps.game.models import GameProgress as GP
    entry.total_score = player.total_score
    entry.levels_completed = GP.objects.filter(
        player=player, completed=True
    ).count()
    entry.save(update_fields=["total_score", "levels_completed", "updated_at"])

    # Пересчитать ранги всех игроков
    LeaderboardEntry.recalculate_ranks()
```

```python
# backend/apps/leaderboard/models.py (фрагмент)
class LeaderboardEntry(models.Model):
    player = models.OneToOneField("accounts.Player", on_delete=models.CASCADE)
    total_score = models.PositiveIntegerField(default=0)
    levels_completed = models.PositiveSmallIntegerField(default=0)
    achievements_count = models.PositiveSmallIntegerField(default=0)
    rank = models.PositiveIntegerField(default=0, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def recalculate_ranks(cls) -> None:
        """Пересчитать ранги всех игроков по total_score."""
        entries = cls.objects.order_by("-total_score")
        for rank, entry in enumerate(entries, start=1):
            if entry.rank != rank:
                cls.objects.filter(pk=entry.pk).update(rank=rank)
```

### 3.2.6. Административная панель Unfold

Unfold предоставляет современный Material Design интерфейс для Django Admin. Пример конфигурации:

```python
# backend/config/settings/base.py (секция UNFOLD)
UNFOLD = {
    "SITE_TITLE": "EcoGame Admin",
    "SITE_HEADER": "EcoGame — Ekologik O'yin Boshqaruvi",
    "COLORS": {
        "primary": {
            "50": "236 253 245",
            "500": "16 185 129",   # emerald-500 — природный зелёный
            "900": "6 78 59",
        }
    },
}
```

```python
# backend/apps/game/admin.py (фрагмент)
from unfold.admin import ModelAdmin

@admin.register(EcoAction)
class EcoActionAdmin(ModelAdmin):
    list_display = ["key", "name_uz", "category", "score_value", "unlock_level"]
    list_filter = ["category", "unlock_level"]
    search_fields = ["key", "name_uz"]
    list_per_page = 25
```

---

## 3.3. Реализация клиентской части (Frontend)

### 3.3.1. API-клиент с автоматическим обновлением токенов

```typescript
// frontend/src/api/client.ts
import axios from "axios";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1",
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const refresh = localStorage.getItem("refresh_token");
        const { data } = await axios.post(
          `${apiClient.defaults.baseURL}/auth/token/refresh/`,
          { refresh }
        );
        localStorage.setItem("access_token", data.access);
        original.headers.Authorization = `Bearer ${data.access}`;
        return apiClient(original);
      } catch {
        // refresh истёк — разлогиниваем
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);
```

**Ключевой паттерн**: флаг `_retry` предотвращает бесконечную рекурсию при повторном 401 после обновления токена.

### 3.3.2. Zustand Store — управление состоянием игры

```typescript
// frontend/src/stores/gameStore.ts (фрагмент)
interface GameState {
  currentLevel: Level | null;
  currentSession: GameSession | null;
  ecosystem: EcosystemState;
  score: number;
  // ...методы
}

export const useGameStore = create<GameState>((set, get) => ({
  currentLevel: null,
  currentSession: null,
  ecosystem: { air: 0, water: 0, soil: 0, biodiversity: 0 },
  score: 0,

  startGame: async (levelId: number) => {
    const { data: level } = await gameApi.getLevel(levelId);
    const { data: session } = await gameApi.startSession(levelId);
    set({
      currentLevel: level,
      currentSession: session,
      ecosystem: level.ecosystem_initial,
      score: 0,
      isPlaying: true,
    });
    return session;
  },

  setProgress: (progress: GameProgress) => {
    set({
      score: progress.score,
      ecosystem: {
        air: progress.air_quality,
        water: progress.water_purity,
        soil: progress.soil_health,
        biodiversity: progress.biodiversity,
      },
    });
  },
}));
```

### 3.3.3. Интеграция Phaser.js с React через EventBus

Центральная архитектурная задача — обеспечить двустороннюю связь между React (управление состоянием) и Phaser.js (игровой движок). Использован паттерн **EventBus** на основе `Phaser.Events.EventEmitter`:

```typescript
// frontend/src/game/events/EventBus.ts
import Phaser from "phaser";

export const EventBus = new Phaser.Events.EventEmitter();

export const EVENTS = {
  SCORE_UPDATED: "score-updated",
  ECOSYSTEM_CHANGED: "ecosystem-changed",
  ACTION_PERFORMED: "action-performed",
  ACHIEVEMENT_UNLOCKED: "achievement-unlocked",
  LEVEL_COMPLETED: "level-completed",
} as const;
```

```typescript
// frontend/src/game/PhaserGame.tsx (фрагмент)
export function PhaserGame({ levelId, levelConfig, onGameEvent }: PhaserGameProps) {
  const gameRef = useRef<Phaser.Game | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || gameRef.current) return;

    const config: Phaser.Types.Core.GameConfig = {
      type: Phaser.AUTO,
      parent: containerRef.current,
      width: 800, height: 600,
      scene: [BootScene, PreloadScene, MainScene, HUDScene],
      physics: { default: "arcade" },
      scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
    };

    const game = new Phaser.Game(config);
    game.registry.set("levelConfig", levelConfig);  // передаём данные в сцены
    gameRef.current = game;

    // Мост: Phaser → React через EventBus
    EventBus.on(EVENTS.ECOSYSTEM_CHANGED, (data: EcosystemState) => {
      onGameEvent("ecosystem-changed", data);
    });
    EventBus.on(EVENTS.SCORE_UPDATED, (data: { score: number }) => {
      onGameEvent("score-updated", data);
    });

    return () => {
      EventBus.removeAllListeners();
      game.destroy(true);     // полная очистка WebGL-контекста
      gameRef.current = null;
    };
  }, []);                     // deps пустой — один раз при маунте

  return <div ref={containerRef} style={{ width: "100%", height: "100%" }} />;
}
```

**Почему `useRef`, а не `useState`**: Phaser.Game — мутабельный объект с собственным lifecycle. `useState` вызвал бы лишние ре-рендеры при изменении инстанса; `useRef` хранит ссылку без реакции React.

### 3.3.4. Сцены Phaser.js

**Иерархия сцен**:
```
BootScene → PreloadScene → MainScene
                              ↓ (запускает параллельно)
                           HUDScene
```

```typescript
// frontend/src/game/scenes/MainScene.ts (фрагмент create())
export class MainScene extends Phaser.Scene {
  private ecosystemManager!: EcosystemManager;
  private actionSystem!: ActionSystem;

  create(): void {
    const levelConfig: Level = this.registry.get("levelConfig");

    // Фон — цвет неба (обновляется в update())
    this.cameras.main.setBackgroundColor("#87CEEB");

    // Создать интерактивные зоны из конфига уровня
    const zones = levelConfig.map_config?.zones ?? [];
    zones.forEach((zone: MapZone) => {
      this.createInteractiveZone(zone);
    });

    // Инициализировать системы
    this.ecosystemManager = new EcosystemManager(levelConfig.ecosystem_initial);
    this.actionSystem = new ActionSystem(this, this.ecosystemManager);

    // Запустить HUD параллельно
    this.scene.launch("HUDScene");
  }

  update(_time: number, delta: number): void {
    this.ecosystemManager.tick(delta);

    // Визуальное отображение состояния воздуха
    const air = this.ecosystemManager.getState().air;
    const skyColor = Phaser.Display.Color.Interpolate.ColorWithColor(
      { r: 128, g: 128, b: 128 } as Phaser.Display.Color,  // серый (загрязнённый)
      { r: 135, g: 206, b: 235 } as Phaser.Display.Color,  // голубой (чистый)
      100, air
    );
    this.cameras.main.setBackgroundColor(
      Phaser.Display.Color.RGBToString(skyColor.r, skyColor.g, skyColor.b)
    );
  }
}
```

### 3.3.5. EcosystemManager — симуляция экосистемы

```typescript
// frontend/src/game/systems/EcosystemManager.ts (фрагмент)
export class EcosystemManager {
  private state: EcosystemState;
  private tickAccumulator = 0;

  constructor(initialState: EcosystemState) {
    this.state = { ...initialState };
  }

  tick(delta: number): void {
    this.tickAccumulator += delta;
    if (this.tickAccumulator < 1000) return;  // раз в секунду

    const seconds = this.tickAccumulator / 1000;
    this.tickAccumulator = 0;

    // Пассивная деградация
    this.state.air = Math.max(0, this.state.air - 0.02 * seconds);
    this.state.water = Math.max(0, this.state.water - 0.015 * seconds);
    this.state.soil = Math.max(0, this.state.soil - 0.01 * seconds);
    this.state.biodiversity = Math.max(0, this.state.biodiversity - 0.025 * seconds);

    // Compound-эффект биоразнообразия
    if (this.state.biodiversity > 50) {
      const bonus = ((this.state.biodiversity - 50) / 10) * 0.005;
      this.state.air = Math.min(100, this.state.air + bonus);
      this.state.water = Math.min(100, this.state.water + bonus);
      this.state.soil = Math.min(100, this.state.soil + bonus * 1.5);
    }

    EventBus.emit(EVENTS.ECOSYSTEM_CHANGED, { ...this.state });
  }
}
```

### 3.3.6. Синхронизация прогресса с сервером

```typescript
// frontend/src/hooks/useGameSync.ts (фрагмент)
export function useGameSync(sessionId: number | null) {
  const actionBuffer = useRef<ActionItem[]>([]);  // useRef! не useState
  const { setProgress } = useGameStore();

  const flushBuffer = useCallback(async () => {
    if (!sessionId || actionBuffer.current.length === 0) return;
    const actions = [...actionBuffer.current];
    actionBuffer.current = [];
    try {
      const { data: progress } = await gameApi.submitActions(sessionId, actions);
      setProgress(progress);
    } catch {
      // Повторная постановка в очередь при ошибке сети
      actionBuffer.current = [...actions, ...actionBuffer.current];
    }
  }, [sessionId, setProgress]);

  useEffect(() => {
    const interval = setInterval(flushBuffer, 15_000);
    return () => {
      clearInterval(interval);
      flushBuffer();    // отправить остаток при анмаунте
    };
  }, [flushBuffer]);

  return {
    pushAction: (action: ActionItem) => {
      actionBuffer.current.push(action);
    },
    flushBuffer,
  };
}
```

**Почему `useRef` для буфера**: `setInterval` захватывает значение переменной в closure на момент создания. При использовании `useState` интервал всегда видит стартовое значение буфера (пустой массив). `useRef.current` всегда указывает на актуальное значение, т.к. мутация ref не вызывает ре-рендер.

---

## 3.4. Локализация на узбекский язык

### 3.4.1. Подход к i18n

Для упрощения использована собственная минималистичная реализация переводов без тяжёлых библиотек (i18next, react-intl):

```typescript
// frontend/src/i18n/index.ts
import uz from "./uz.json";

type NestedKeys<T, Prefix extends string = ""> = {
  [K in keyof T]: T[K] extends object
    ? NestedKeys<T[K], `${Prefix}${K & string}.`>
    : `${Prefix}${K & string}`;
}[keyof T];

export function t(key: string): string {
  const keys = key.split(".");
  let value: unknown = uz;
  for (const k of keys) {
    if (typeof value !== "object" || value === null) return key;
    value = (value as Record<string, unknown>)[k];
  }
  return typeof value === "string" ? value : key;
}
```

```json
// frontend/src/i18n/uz.json (фрагмент)
{
  "app_name": "EcoGame",
  "game": {
    "air_quality": "Havo sifati",
    "water_purity": "Suv tozaligi",
    "soil_health": "Tuproq holati",
    "biodiversity": "Biologik xilma-xillik",
    "score": "Ball",
    "start": "Boshlash",
    "pause": "Pauza",
    "level_complete": "Daraja yakunlandi!"
  },
  "achievements": {
    "unlocked": "Yutuq ochildi"
  }
}
```

### 3.4.2. Образовательный контент на узбекском

Все фикстуры написаны на литературном узбекском языке:

```json
// backend/fixtures/educational_content.json (фрагмент)
{
  "model": "education.educationalcontent",
  "fields": {
    "title_uz": "Orol dengizi muammosi va uning oqibatlari",
    "body_uz": "Orol dengizi — bir zamonlar dunyodagi to'rtinchi eng katta ko'l edi...",
    "category": "WATER",
    "order": 1,
    "is_published": true
  }
}
```

---

## 3.5. Контейнеризация и развёртывание

### 3.5.1. Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Установить uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Установить зависимости (кэшируется при неизменном uv.lock)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Копировать код
COPY . .

# Собрать статику Django
RUN uv run python manage.py collectstatic --noinput \
    --settings=config.settings.prod

EXPOSE 8000
CMD ["uv", "run", "gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
```

**Multi-stage caching**: зависимости (`pyproject.toml` + `uv.lock`) копируются отдельно от кода. Docker кэширует слой с `uv sync` при неизменных lock-файлах — пересборка занимает секунды вместо минут.

### 3.5.2. Frontend Dockerfile (multi-stage)

```dockerfile
# frontend/Dockerfile
# Стадия 1: сборка React+TypeScript приложения
FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --prefer-offline          # детерминированная установка

COPY . .
ARG VITE_API_URL=/api/v1            # инжектируется через docker-compose args
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build                   # генерирует /app/dist/

# Стадия 2: раздача статики через Nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

```nginx
# frontend/nginx.conf (SPA fallback)
server {
    listen 80;
    root /usr/share/nginx/html;
    
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        try_files $uri $uri/ /index.html;  # SPA fallback для React Router
    }
}
```

### 3.5.3. Nginx Reverse Proxy

```nginx
# nginx/nginx.conf
upstream backend { server backend:8000; }
upstream frontend { server frontend:80; }

server {
    listen 80;
    server_name ecogame.fullfocus.dev;
    client_max_body_size 10M;

    location /static/ {
        alias /app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /admin/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
    }
}
```

### 3.5.4. Docker Compose (Production)

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-ecogame}
      POSTGRES_USER: ${POSTGRES_USER:-ecogame}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-ecogame}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    env_file: .env
    environment:
      DJANGO_SETTINGS_MODULE: config.settings.prod
    volumes:
      - static_volume:/app/static_collected
      - media_volume:/app/media
    depends_on:
      postgres:
        condition: service_healthy   # ждёт pg_isready перед стартом
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        VITE_API_URL: /api/v1        # относительный путь — через nginx
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    build:
      context: ./nginx
      dockerfile: Dockerfile
    ports:
      - "80:80"
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
```

**`depends_on: condition: service_healthy`**: Gunicorn не стартует до успешного `pg_isready` — предотвращает ошибки соединения при холодном старте.

### 3.5.5. Coolify и CI/CD

Coolify (self-hosted PaaS) настроен на автодеплой при push в ветку `main` GitHub-репозитория. Конфигурация хранится исключительно в Coolify dashboard — никакие секреты не вносятся в Git-репозиторий.

Процесс деплоя:
1. `git push origin main` → GitHub webhook → Coolify
2. Coolify клонирует репозиторий на сервере
3. `docker compose up --build -d` — пересобирает изменённые сервисы
4. Healthcheck postgres → start backend → start frontend → start nginx
5. Let's Encrypt обновляет SSL-сертификат (автоматически через Caddy/Nginx)

---

## 3.6. Выводы по Главе 3

В данной главе описана реализация всех компонентов системы EcoGame:

1. **Backend** (Django 5.1 + DRF): split-settings архитектура, кастомная модель Player, GameService с транзакционными операциями, денормализованный LeaderboardEntry через Django signals, 20 REST API эндпоинтов, административная панель Unfold.

2. **Frontend** (React 19 + TypeScript + Zustand): строготипизированный API-клиент с автообновлением JWT, EventBus-паттерн для интеграции Phaser.js с React, hook useGameSync с буфером действий на useRef.

3. **Phaser.js**: 4-сценная архитектура (Boot → Preload → Main + HUD), EcosystemManager с деградацией и compound-эффектами, ActionSystem с InteractiveZones.

4. **Локализация**: полный перевод интерфейса и контента на узбекский язык через собственный минималистичный i18n-слой.

5. **Деплой**: многоступенчатые Docker-образы, 4-сервисный Docker Compose с healthcheck, Nginx reverse proxy, Coolify на собственном сервере с Let's Encrypt SSL.

---

*Объём главы: ~18 страниц (Times New Roman 14pt, 1.5 интервал)*
