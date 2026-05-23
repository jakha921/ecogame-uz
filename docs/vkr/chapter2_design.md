# Глава 2. Проектирование системы EcoGame

## 2.1. Архитектура приложения

### 2.1.1. Общая архитектура

EcoGame построена по классической клиент-серверной архитектуре с чётким разделением ответственности между четырьмя логическими слоями:

```
┌─────────────────────────────────────────────────┐
│                  КЛИЕНТ (Browser)                │
│  ┌─────────────────┐   ┌──────────────────────┐  │
│  │   React 19 SPA   │   │   Phaser.js 3 Game   │  │
│  │  (UI / Routing)  │◄─►│  (Game Engine)       │  │
│  │  Zustand Store   │   │  EventBus Bridge     │  │
│  └────────┬─────────┘   └──────────────────────┘  │
└───────────┼─────────────────────────────────────┘
            │ HTTP/REST (JSON)
            │ JWT Bearer Token
┌───────────▼─────────────────────────────────────┐
│                  NGINX (Reverse Proxy)           │
│  /api/* → backend:8000   / → frontend:80         │
└───────────┬────────────────┬────────────────────┘
            │                │
┌───────────▼──┐    ┌────────▼────────────────────┐
│  Django 5.1  │    │  React+Nginx (Static SPA)   │
│  + DRF       │    │  /usr/share/nginx/html       │
│  + Gunicorn  │    └─────────────────────────────┘
│  (3 workers) │
└───────────┬──┘
            │ Django ORM
┌───────────▼──┐
│ PostgreSQL 16│
│ (prod) /     │
│ SQLite (dev) │
└──────────────┘
```

Все компоненты работают в отдельных Docker-контейнерах, управляемых Docker Compose.

### 2.1.2. Диаграмма компонентов

```mermaid
graph TB
    subgraph "Docker Compose"
        NGINX["nginx:alpine\nReverse Proxy\n:80"]
        FRONTEND["node:20-alpine → nginx:alpine\nReact SPA + Phaser.js\n(static)"]
        BACKEND["python:3.12-slim\nDjango 5.1 + DRF\nGunicorn :8000"]
        DB["postgres:16-alpine\nPostgreSQL\n:5432"]
    end

    USER["Браузер\n(Пользователь)"] --> NGINX
    NGINX -- "/api/*, /admin/*" --> BACKEND
    NGINX -- "/ (SPA)" --> FRONTEND
    BACKEND --> DB

    subgraph "Клиентская часть (браузер)"
        REACT["React 19\nZustand Store\nReact Router v7"]
        PHASER["Phaser.js 3.80\nBootScene\nPreloadScene\nMainScene\nHUDScene"]
        EVENTBUS["EventBus\n(Phaser.Events.EventEmitter)"]

        REACT <--> EVENTBUS
        PHASER --> EVENTBUS
    end
```

### 2.1.3. Диаграмма развёртывания

```mermaid
graph LR
    subgraph "Разработчик"
        DEV["MacOS / Linux\ngit push"]
    end

    subgraph "GitHub"
        REPO["github.com/jakha921/ecogame-uz\nprivate repository"]
    end

    subgraph "Сервер 89.167.60.96"
        subgraph "Coolify (self-hosted PaaS)"
            COOLIFY["Coolify Dashboard\ncoolify.fullfocus.dev"]
        end
        subgraph "Docker Compose Stack"
            NGINX2["nginx:alpine\n:80 → :443"]
            BACKEND2["Django + Gunicorn\n:8000"]
            FRONTEND2["React SPA\n:80"]
            PG["PostgreSQL 16\n:5432"]
        end
        SSL["Let's Encrypt\nSSL Certificate"]
    end

    DNS["DNS\necogame.fullfocus.dev\n→ 89.167.60.96"]

    DEV --> REPO
    REPO --> COOLIFY
    COOLIFY --> NGINX2
    NGINX2 --- SSL
    NGINX2 --> BACKEND2
    NGINX2 --> FRONTEND2
    BACKEND2 --> PG
    DNS --> NGINX2
```

---

## 2.2. Проектирование базы данных

### 2.2.1. ER-диаграмма

```mermaid
erDiagram
    Player {
        int id PK
        varchar username UK
        varchar nickname UK
        varchar email
        varchar password_hash
        varchar avatar
        int total_score
        datetime date_joined
    }

    Level {
        int id PK
        int number UK
        varchar name_uz
        text description_uz
        int required_score
        json map_config
        json ecosystem_initial
    }

    EcoAction {
        int id PK
        varchar key UK
        varchar name_uz
        text description_uz
        varchar category
        int score_value
        float air_impact
        float water_impact
        float soil_impact
        float biodiversity_impact
        int cooldown_seconds
        int unlock_level_id FK
        varchar sprite_key
    }

    GameSession {
        int id PK
        int player_id FK
        int level_id FK
        datetime started_at
        datetime ended_at
        bool is_active
    }

    GameProgress {
        int id PK
        int player_id FK
        int level_id FK
        int score
        float air_quality
        float water_purity
        float soil_health
        float biodiversity
        json actions_performed
        bool completed
        datetime completed_at
        datetime updated_at
    }

    ActionLog {
        int id PK
        int session_id FK
        int action_id FK
        datetime performed_at
        float position_x
        float position_y
        json result_delta
    }

    Achievement {
        int id PK
        varchar key UK
        varchar name_uz
        text description_uz
        varchar icon
        varchar condition_type
        json condition_value
    }

    PlayerAchievement {
        int id PK
        int player_id FK
        int achievement_id FK
        datetime unlocked_at
    }

    EducationalContent {
        int id PK
        varchar title_uz
        text body_uz
        varchar category
        varchar image
        int order
        bool is_published
        datetime created_at
    }

    EcoFact {
        int id PK
        varchar text_uz
        varchar source
        varchar category
    }

    LeaderboardEntry {
        int id PK
        int player_id FK
        int total_score
        int levels_completed
        int achievements_count
        int rank
        datetime updated_at
    }

    Player ||--o{ GameSession : "играет"
    Player ||--o{ GameProgress : "прогресс"
    Player ||--o{ PlayerAchievement : "разблокирует"
    Player ||--|| LeaderboardEntry : "рейтинг"

    Level ||--o{ GameSession : "содержит"
    Level ||--o{ GameProgress : "имеет"
    Level ||--o{ EcoAction : "unlock_level"

    GameSession ||--o{ ActionLog : "записывает"
    EcoAction ||--o{ ActionLog : "выполняется"

    Achievement ||--o{ PlayerAchievement : "присваивается"
```

### 2.2.2. Описание сущностей

| Сущность | Назначение | Ключевые поля |
|----------|------------|---------------|
| `Player` | Кастомная модель пользователя (extends AbstractUser) | `nickname`, `total_score`, `avatar` |
| `Level` | Игровые уровни с конфигурацией карты | `map_config` (JSON), `ecosystem_initial` (JSON) |
| `EcoAction` | Каталог экологических действий | `*_impact` (float), `cooldown_seconds` |
| `GameSession` | Игровая сессия (один запуск уровня) | `started_at`, `ended_at`, `is_active` |
| `GameProgress` | Агрегированный прогресс игрока по уровню | `air_quality`, `water_purity`, `soil_health`, `biodiversity` |
| `ActionLog` | Лог каждого отдельного действия | `position_x/y`, `result_delta` (JSON) |
| `Achievement` | Определения достижений | `condition_type`, `condition_value` (JSON) |
| `PlayerAchievement` | M2M связь игрок-достижение | `unlocked_at` |
| `EducationalContent` | Образовательные статьи | `title_uz`, `body_uz`, `category` |
| `EcoFact` | Краткие экологические факты | `text_uz`, `source` |
| `LeaderboardEntry` | Денормализованная таблица лидеров | `rank`, `total_score` (обновляется сигналами) |

### 2.2.3. Архитектурные решения базы данных

**Денормализация LeaderboardEntry**: вместо вычисления рейтинга запросом `ORDER BY total_score` по всей таблице `Player` (O(n log n)), используется предвычисленная таблица `LeaderboardEntry`, обновляемая Django signals при изменении `GameProgress` или `PlayerAchievement`. Это обеспечивает O(1) чтение при просмотре лидерборда.

**JSONField для гибких конфигов**: `Level.map_config` и `Level.ecosystem_initial` хранятся в JSON, что позволяет изменять структуру карты и начальные параметры экосистемы без миграций схемы БД.

**unique_together**: `GameProgress(player, level)` — одна запись прогресса на уникальную пару игрок+уровень; `PlayerAchievement(player, achievement)` — предотвращает дублирование достижений.

---

## 2.3. Проектирование REST API

### 2.3.1. Таблица эндпоинтов

| Метод | Путь | Описание | Авторизация |
|-------|------|----------|-------------|
| `POST` | `/api/v1/auth/register/` | Регистрация игрока | AllowAny |
| `POST` | `/api/v1/auth/login/` | Получение JWT токенов | AllowAny |
| `POST` | `/api/v1/auth/token/refresh/` | Обновление access токена | AllowAny |
| `GET` | `/api/v1/auth/me/` | Профиль текущего игрока | IsAuthenticated |
| `PATCH` | `/api/v1/auth/me/` | Обновление профиля | IsAuthenticated |
| `GET` | `/api/v1/game/levels/` | Список уровней | AllowAny |
| `GET` | `/api/v1/game/levels/{id}/` | Детали уровня | AllowAny |
| `GET` | `/api/v1/game/actions/` | Список экодействий | IsAuthenticated |
| `GET` | `/api/v1/game/progress/` | Прогресс по всем уровням | IsAuthenticated |
| `GET` | `/api/v1/game/progress/{level_id}/` | Прогресс по уровню | IsAuthenticated |
| `POST` | `/api/v1/game/sessions/start/` | Начать сессию | IsAuthenticated |
| `POST` | `/api/v1/game/sessions/{id}/end/` | Завершить сессию | IsAuthenticated |
| `POST` | `/api/v1/game/sessions/{id}/actions/` | Отправить батч действий | IsAuthenticated |
| `GET` | `/api/v1/game/achievements/` | Все достижения | IsAuthenticated |
| `GET` | `/api/v1/game/achievements/my/` | Мои достижения | IsAuthenticated |
| `GET` | `/api/v1/education/articles/` | Образовательные статьи | AllowAny |
| `GET` | `/api/v1/education/articles/{id}/` | Детали статьи | AllowAny |
| `GET` | `/api/v1/education/facts/random/` | Случайный эко-факт | AllowAny |
| `GET` | `/api/v1/leaderboard/` | Таблица лидеров (top 50) | AllowAny |
| `GET` | `/api/v1/leaderboard/me/` | Мой ранг | IsAuthenticated |

### 2.3.2. Примеры запросов и ответов

**Регистрация:**
```json
POST /api/v1/auth/register/
{
  "username": "jahongir_r",
  "nickname": "Jahon",
  "email": "jahongir@example.com",
  "password": "secure_pass",
  "password_confirm": "secure_pass"
}
→ 201 Created
{
  "id": 1,
  "username": "jahongir_r",
  "nickname": "Jahon",
  "email": "jahongir@example.com",
  "avatar": "default",
  "total_score": 0,
  "date_joined": "2024-06-01T10:00:00Z"
}
```

**Батч экодействий:**
```json
POST /api/v1/game/sessions/1/actions/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
{
  "actions": [
    {"action_key": "plant_tree", "position_x": 120.5, "position_y": 200.0},
    {"action_key": "clean_water", "position_x": 350.0, "position_y": 180.0}
  ]
}
→ 200 OK
{
  "id": 1,
  "player": 1,
  "level": 1,
  "score": 150,
  "air_quality": 35.6,
  "water_purity": 42.1,
  "soil_health": 22.0,
  "biodiversity": 18.5,
  "actions_performed": {"plant_tree": 1, "clean_water": 1},
  "completed": false
}
```

### 2.3.3. JWT-аутентификация

```mermaid
sequenceDiagram
    participant C as Клиент (React)
    participant N as Nginx
    participant B as Django Backend
    participant DB as PostgreSQL

    C->>N: POST /api/v1/auth/login/ {username, password}
    N->>B: проксирует запрос
    B->>DB: проверка учётных данных
    DB-->>B: Player объект
    B-->>N: {access: "eyJ...", refresh: "eyJ..."}
    N-->>C: токены (access 1ч, refresh 7д)

    Note over C: сохраняет в localStorage

    C->>N: GET /api/v1/auth/me/ Authorization: Bearer eyJ...
    N->>B: проксирует с токеном
    B->>B: верифицирует JWT (без DB запроса)
    B-->>C: данные профиля

    Note over C: access токен истёк

    C->>N: POST /api/v1/auth/token/refresh/ {refresh: "eyJ..."}
    N->>B: проксирует
    B->>DB: проверка refresh токена
    B-->>C: новый access токен
```

---

## 2.4. Проектирование игровой механики

### 2.4.1. Концепция экосимулятора

EcoGame реализует упрощённую модель экосистемы, описываемую четырьмя индикаторами:

| Индикатор | Диапазон | Реальная аналогия | Визуальный эффект |
|-----------|----------|------------------|-------------------|
| `air_quality` | 0–100 | Индекс качества воздуха (AQI инвертированный) | Цвет неба (серый → голубой) |
| `water_purity` | 0–100 | Степень чистоты водоёмов | Цвет воды (коричневый → голубой) |
| `soil_health` | 0–100 | Плодородие почвы | Цвет земли (серый → зелёный) |
| `biodiversity` | 0–100 | Количество видов флоры и фауны | Появление животных |

**Формула деградации** (пассивное ухудшение при бездействии):
```
air_quality     -= 0.020 × (delta_ms / 1000)
water_purity    -= 0.015 × (delta_ms / 1000)
soil_health     -= 0.010 × (delta_ms / 1000)
biodiversity    -= 0.025 × (delta_ms / 1000)
```

**Compound-эффект** (биоразнообразие улучшает остальные индикаторы):
```
if biodiversity > 50:
    bonus = (biodiversity - 50) / 10 × 0.005
    air_quality += bonus
    water_purity += bonus
    soil_health += bonus × 1.5
```

**Условие завершения уровня**:
```
completed = (air_quality >= 80) AND (water_purity >= 80)
          AND (soil_health >= 80) AND (biodiversity >= 80)
```

### 2.4.2. Система уровней

| № | Название (uz) | Масштаб | Начальные индикаторы | Требуемые очки |
|---|--------------|---------|---------------------|----------------|
| 1 | Kichik hovli | Маленький двор | air:30, water:25, soil:20, bio:15 | 0 |
| 2 | Mahalla | Район | air:20, water:18, soil:15, bio:10 | 500 |
| 3 | Shahar | Город | air:15, water:12, soil:10, bio:8 | 1500 |
| 4 | Viloyat | Область | air:10, water:8, soil:7, bio:5 | 3000 |

С ростом масштаба снижаются начальные значения индикаторов и увеличивается скорость деградации, что требует более стратегического подхода.

### 2.4.3. Система экологических действий

| Действие (uz) | Категория | Очки | Влияние на индикаторы |
|--------------|-----------|------|----------------------|
| Daraxt ekish | FLORA | 50 | air+3, soil+2, bio+2 |
| Gul ekish | FLORA | 20 | air+1, soil+1, bio+1 |
| Suvni tozalash | WATER | 60 | water+4, bio+1 |
| Suv tejash | WATER | 30 | water+2 |
| Chiqindilarni saralash | WASTE | 40 | soil+3, air+1 |
| Qayta ishlash | WASTE | 35 | soil+2, air+2 |
| Quyosh paneli o'rnatish | ENERGY | 80 | air+5 |
| Energiya tejash | ENERGY | 25 | air+2 |
| Hayvonlarni himoya qilish | FAUNA | 70 | bio+5 |
| Qushlar uchun uy | FAUNA | 40 | bio+3 |
| Baliqlarni saqlash | FAUNA | 55 | water+2, bio+4 |
| Bog' parvarish qilish | FLORA | 30 | air+2, soil+3, bio+1 |

### 2.4.4. Диаграмма состояний игры

```mermaid
stateDiagram-v2
    [*] --> MainMenu: открыть приложение

    MainMenu --> LevelSelect: нажать "O'ynash"
    LevelSelect --> Loading: выбрать уровень

    Loading --> BootScene: Phaser.Game создан
    BootScene --> PreloadScene: ассеты логотипа загружены
    PreloadScene --> MainScene: все ассеты загружены

    state "Игровой процесс" as Gameplay {
        MainScene --> Paused: нажать паузу
        Paused --> MainScene: возобновить
        MainScene --> ActionMenu: клик по зоне
        ActionMenu --> MainScene: отмена
        ActionMenu --> PerformingAction: выбрать действие
        PerformingAction --> MainScene: анимация завершена
    }

    MainScene --> LevelCompleted: все индикаторы >= 80
    LevelCompleted --> MainMenu: нажать "Bosh sahifaga"

    MainScene --> GameExit: нажать выход
    GameExit --> MainMenu: подтверждение
```

### 2.4.5. Use Case диаграмма

```mermaid
graph LR
    subgraph "Акторы"
        GUEST["Гость"]
        PLAYER["Зарегистрированный\nигрок"]
        ADMIN["Администратор"]
    end

    subgraph "Функциональность системы"
        UC1["Просмотр уровней"]
        UC2["Просмотр образовательных статей"]
        UC3["Просмотр лидерборда"]
        UC4["Регистрация / Вход"]
        UC5["Игра (выполнение экодействий)"]
        UC6["Получение достижений"]
        UC7["Просмотр своего рейтинга"]
        UC8["Редактирование профиля"]
        UC9["Управление контентом (Admin)"]
        UC10["Управление игроками (Admin)"]
    end

    GUEST --> UC1
    GUEST --> UC2
    GUEST --> UC3
    GUEST --> UC4

    PLAYER --> UC1
    PLAYER --> UC2
    PLAYER --> UC3
    PLAYER --> UC5
    PLAYER --> UC6
    PLAYER --> UC7
    PLAYER --> UC8

    ADMIN --> UC9
    ADMIN --> UC10
    ADMIN --> UC1
    ADMIN --> UC2
```

### 2.4.6. Система достижений

| Ключ | Название (uz) | Условие | Тип условия |
|------|--------------|---------|-------------|
| first_tree | Birinchi daraxt | Посадить 1 дерево | ACTION_COUNT |
| gardener | Bog'bon | Посадить 10 деревьев | ACTION_COUNT |
| water_guardian | Suv qo'riqchisi | Очистить воду 5 раз | ACTION_COUNT |
| eco_score_1k | Ekolog | Набрать 1000 очков | SCORE |
| level_1_done | Tabiat do'sti | Завершить уровень 1 | LEVEL_COMPLETE |
| air_master | Havo xo'jayini | Довести air_quality до 90 | INDICATOR |
| multi_action | Faol ekolog | 20 действий за сессию | ACTION_COUNT |
| biodiversity_king | Tabiat podshosi | Biodiversity >= 90 | INDICATOR |
| all_actions | Har tomonlama | Выполнить все 5 категорий | ACTION_COUNT |
| level_4_done | O'zbek ekolog | Завершить уровень 4 | LEVEL_COMPLETE |

---

## 2.5. Проектирование пользовательского интерфейса

### 2.5.1. Карта экранов

```mermaid
graph TD
    ENTRY["Открыть ecogame.fullfocus.dev"]

    ENTRY --> HOME["/ — Главная\n(MainMenu)\nУровни + Статистика"]
    ENTRY --> LOGIN["/login — Вход"]
    ENTRY --> REGISTER["/register — Регистрация"]

    HOME --> GAME["/play/:levelId — Игра\n(ProtectedRoute)"]
    HOME --> LEADER["/leaderboard — Лидерборд"]
    HOME --> EDUCATION["/education — Образование"]
    HOME --> PROFILE["/profile — Профиль\n(ProtectedRoute)"]

    EDUCATION --> EDU_DETAIL["/education/:id\nДеталь статьи"]

    LOGIN --> HOME
    REGISTER --> HOME
```

### 2.5.2. Wireframes ключевых экранов

**MainMenu:**
```
╔════════════════════════════════════════╗
║    🌿 EcoGame — Ekologik o'yin        ║
╠════════════════════════════════════════╣
║  [Bosh sahifa] [O'ynash] [Yetakchilar] [Ta'lim] │ [Kirish] ║
╠════════════════════════════════════════╣
║                                        ║
║  Sizning natijangiz: 1250 ball        ║
║  Darajalar:                           ║
║  ┌──────────┐ ┌──────────┐           ║
║  │ 🏡 1    │ │ 🏘️ 2    │           ║
║  │ Kichik  │ │ Mahalla  │           ║
║  │ hovli   │ │ 🔒 500 ★│           ║
║  │[Boshlash]│ │ [Boshlash]│          ║
║  └──────────┘ └──────────┘           ║
║  ┌──────────┐ ┌──────────┐           ║
║  │ 🏙️ 3   │ │ 🗺️ 4    │           ║
║  │ Shahar  │ │ Viloyat  │           ║
║  │ 🔒 1500★│ │ 🔒 3000★│           ║
║  └──────────┘ └──────────┘           ║
║                                        ║
║  💡 Bugungi fakt: Bitta daraxt       ║
║     yiliga 22 kg CO₂ shimadi         ║
╚════════════════════════════════════════╝
```

**GamePage (во время игры):**
```
╔════════════════════════════════════════╗
║ Havo: ████░░░░ 45%  Suv: ██████░░ 60% ║
║ Tuproq: ███░░░░░ 35% Bio: ██░░░░░░ 25%║
║                              Ball: 350 ║
╠════════════════════════════════════════╣
║                                        ║
║    [  Phaser.js Canvas 800×500  ]     ║
║    [ Интерактивная карта уровня ]     ║
║    [  InteractiveZones + Объекты ]    ║
║                                        ║
╠════════════════════════════════════════╣
║  [⏸ Pauza]                [🚪 Chiqish] ║
╚════════════════════════════════════════╝
```

### 2.5.3. UX-решения

1. **Языковая константа**: все тексты интерфейса на узбекском языке без возможности переключения — целевая аудитория однозначно определена;

2. **Прогрессивное раскрытие**: уровни 2–4 визуально заблокированы (затемнены, иконка 🔒) — исключает confusion при первом запуске;

3. **Немедленная обратная связь**: после каждого экодействия — визуальная анимация (рост дерева, очищение воды) и мгновенное обновление индикаторов в HUD;

4. **Обучение через действие**: первый уровень «Kichik hovli» оформлен как обучающий — интерактивные зоны снабжены подсказками, минимальная деградация;

5. **Адаптивность**: Phaser Scale.FIT обеспечивает корректное отображение на любом экране; React layout адаптирован под мобильные устройства (375px+).

---

## 2.6. Выводы по Главе 2

В данной главе разработана полная проектная документация системы EcoGame:

1. **Архитектура** — клиент-серверная, 4 Docker-контейнера (PostgreSQL, Django/Gunicorn, React/Nginx, Nginx-proxy), связанные через внутреннюю Docker-сеть с единственным публичным портом 80 (→443 через Let's Encrypt).

2. **База данных** — 11 таблиц, спроектированных с учётом нормализации (3НФ) с целенаправленной денормализацией (`LeaderboardEntry`) для обеспечения O(1)-чтения рейтинга.

3. **REST API** — 20 эндпоинтов с JWT-аутентификацией, батч-обработкой действий и чётким разграничением публичных/защищённых ресурсов.

4. **Игровая механика** — экосимулятор с 4 взаимозависимыми индикаторами, пассивной деградацией, compound-эффектами, 12 экодействиями 5 категорий и 10 достижениями.

5. **UI/UX** — 7 экранов на узбекском языке, адаптивный дизайн, принципы прогрессивного раскрытия и немедленной обратной связи.

---

*Объём главы: ~16 страниц (Times New Roman 14pt, 1.5 интервал)*
