# Приложение В. ER-диаграмма базы данных EcoGame

Диаграмма описывает полную схему реляционной базы данных приложения EcoGame
(11 таблиц). Разработана с применением нотации Crow's Foot (ГОСТ не
регламентирует нотацию ER-диаграмм).

```mermaid
erDiagram
    PLAYER {
        int id PK
        varchar username UK
        varchar nickname UK
        varchar email
        varchar avatar
        int total_score
        datetime date_joined
        bool is_active
    }

    LEVEL {
        int id PK
        smallint number UK
        varchar name_uz
        text description_uz
        int required_score
        json map_config
        json ecosystem_initial
    }

    ECO_ACTION {
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

    GAME_SESSION {
        int id PK
        int player_id FK
        int level_id FK
        datetime started_at
        datetime ended_at
        bool is_active
    }

    GAME_PROGRESS {
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

    ACTION_LOG {
        int id PK
        int session_id FK
        int action_id FK
        datetime performed_at
        float position_x
        float position_y
        json result_delta
    }

    ACHIEVEMENT {
        int id PK
        varchar key UK
        varchar name_uz
        text description_uz
        varchar icon
        varchar condition_type
        json condition_value
    }

    PLAYER_ACHIEVEMENT {
        int id PK
        int player_id FK
        int achievement_id FK
        datetime unlocked_at
    }

    EDUCATIONAL_CONTENT {
        int id PK
        varchar title_uz
        text body_uz
        varchar category
        varchar image
        smallint order
        bool is_published
        datetime created_at
    }

    ECO_FACT {
        int id PK
        varchar text_uz
        varchar source
        varchar category
    }

    LEADERBOARD_ENTRY {
        int id PK
        int player_id FK "1-1"
        int total_score
        smallint levels_completed
        smallint achievements_count
        int rank
        datetime updated_at
    }

    PLAYER ||--o{ GAME_SESSION : "plays"
    PLAYER ||--o{ GAME_PROGRESS : "has"
    PLAYER ||--o{ PLAYER_ACHIEVEMENT : "earns"
    PLAYER ||--|| LEADERBOARD_ENTRY : "ranked in"

    LEVEL ||--o{ GAME_SESSION : "hosted in"
    LEVEL ||--o{ GAME_PROGRESS : "tracked by"
    LEVEL ||--o{ ECO_ACTION : "unlocks"

    GAME_SESSION ||--o{ ACTION_LOG : "records"

    ECO_ACTION ||--o{ ACTION_LOG : "logged as"

    ACHIEVEMENT ||--o{ PLAYER_ACHIEVEMENT : "granted via"
```

## Пояснения к схеме

| Таблица | Назначение |
|---------|-----------|
| `PLAYER` | Расширенная модель пользователя Django (AbstractUser) |
| `LEVEL` | Описание уровня: карта, начальные параметры экосистемы |
| `ECO_ACTION` | Каталог экологических действий с коэффициентами влияния |
| `GAME_SESSION` | Факт начала и завершения одной игровой сессии |
| `GAME_PROGRESS` | Накопительный прогресс игрока по уровню (unique: player+level) |
| `ACTION_LOG` | Лог каждого отдельного действия с координатами на карте |
| `ACHIEVEMENT` | Определение достижения и условий его разблокировки |
| `PLAYER_ACHIEVEMENT` | M2M связь игрок ↔ достижение с датой разблокировки |
| `EDUCATIONAL_CONTENT` | Образовательные статьи на узбекском языке |
| `ECO_FACT` | Короткие экологические факты для экранов загрузки |
| `LEADERBOARD_ENTRY` | Денормализованная таблица рейтинга (O(1) чтение) |

## Ключевые архитектурные решения

1. **Денормализованный `LEADERBOARD_ENTRY`**: вместо агрегатного запроса по
   `GAME_PROGRESS` таблица лидеров обновляется Django-сигналами при каждом
   сохранении прогресса. Это обеспечивает O(1) чтение рейтинга при любом
   количестве игроков.

2. **JSONField для `map_config` и `ecosystem_initial`**: позволяет хранить
   гибкую конфигурацию каждого уровня без дополнительных таблиц. PostgreSQL
   обеспечивает нативную поддержку JSONB с индексированием.

3. **`unique_together("player", "level")` в `GAME_PROGRESS`**: гарантирует
   атомарность прогресса — один игрок имеет ровно один экземпляр прогресса
   на каждый уровень. Повторное прохождение обновляет существующую запись.

4. **`result_delta` в `ACTION_LOG`**: снимок изменения индикаторов в момент
   действия позволяет воспроизвести историю сессии и строить аналитику без
   перерасчёта.
